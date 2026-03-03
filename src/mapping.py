import json
from collections import defaultdict
from opentelemetry import trace
from typing import List, Dict, Any


# ---------------------------------------------------------------------------
# C++ enum mirrors  (namespace tracing)
# ---------------------------------------------------------------------------

# operation_type – specifies the type of operation being traced
OP_SEND = 0
OP_RECEIVE = 1
OP_CALLBACK = 2
OP_SHM_HANDSHAKE = 3

OP_TYPE_NAMES = {
    OP_SEND: "send",
    OP_RECEIVE: "receive",
    OP_CALLBACK: "callback_execution",
    OP_SHM_HANDSHAKE: "shm_handshake",
}

# topic_direction – direction of the topic
DIR_PUBLISHER = 0
DIR_SUBSCRIBER = 1

DIR_NAMES = {
    DIR_PUBLISHER: "publisher",
    DIR_SUBSCRIBER: "subscriber",
}

# eTracingLayerType – bitmask for active transport layers
TL_NONE = 0
TL_SHM = 1 << 0   # 1
TL_UDP = 1 << 1   # 2
TL_TCP = 1 << 2   # 4

_LAYER_FLAGS = [
    (TL_SHM, "shm"),
    (TL_UDP, "udp"),
    (TL_TCP, "tcp"),
]


def decode_layer(layer_value: int) -> str:
    """Decode a bitmask ``layer`` value into a human-readable string.

    Examples:
        1  -> "shm"
        3  -> "shm+udp"
        7  -> "shm+udp+tcp"
        0  -> "none"
    """
    if not layer_value:
        return "none"
    parts = [name for flag, name in _LAYER_FLAGS if layer_value & flag]
    return "+".join(parts) if parts else "none"


def load_json_file(filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL file with span data (one JSON object per line)"""
    results = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def build_metadata_lookup(metadata_list: List[Dict]) -> Dict[int, Dict[str, Any]]:
    """Build a lookup from entity_id to metadata attributes"""
    return {meta['entity_id']: meta for meta in metadata_list}


def get_tracing_version(metadata_lookup: Dict[int, Dict[str, Any]]) -> str:
    """Extract the tracing_version from the first metadata entry that has one."""
    for meta in metadata_lookup.values():
        version = meta.get('tracing_version')
        if version:
            return version
    return "unknown"


def set_meta_attributes(span, meta: Dict[str, Any]) -> None:
    """Set common eCAL metadata attributes on a span"""
    if meta:
        for key in ('topic_name', 'type_name', 'encoding', 'host_name',
                     'direction', 'tracing_version'):
            val = meta.get(key, '')
            if val:
                span.set_attribute(f"ecal.{key}", val)


def enrich_spans(spans: List[Dict], metadata_lookup: Dict[int, Dict[str, Any]],
                 id_key: str = 'entity_id') -> None:
    """Pre-merge metadata into each span record to avoid repeated lookups"""
    for span in spans:
        meta = metadata_lookup.get(span[id_key], {})
        span['_meta'] = meta
        span['_topic_name'] = meta.get('topic_name', str(span[id_key]))
        span['_direction'] = meta.get('direction', '')


def _set_common_attributes(span, data: Dict[str, Any], op_type_name: str) -> None:
    """Set the standard set of eCAL attributes on an OTel span."""
    layer_raw = data.get('layer', 0)
    span.set_attribute("ecal.entity_id", data['entity_id'])
    span.set_attribute("ecal.layer", decode_layer(layer_raw))
    span.set_attribute("ecal.layer_raw", layer_raw)
    span.set_attribute("ecal.process_id", data.get('process_id'))
    span.set_attribute("ecal.payload_size", data.get('payload_size'))
    span.set_attribute("ecal.clock", data['clock'])
    span.set_attribute("ecal.op_type", op_type_name)
    topic_id = data.get('topic_id', 0)
    if topic_id:
        span.set_attribute("ecal.topic_id", topic_id)
    set_meta_attributes(span, data['_meta'])


def create_spans_from_data(all_spans: List[Dict],
                           metadata_lookup: Dict[int, Dict[str, Any]],
                           tracer) -> None:
    """Create OpenTelemetry spans from a unified list of eCAL span records.

    Spans are classified as publisher or subscriber based on the ``direction``
    field in their associated metadata entry.  The hierarchy is:

        send  ->  shm_handshake  (same entity_id & clock)
        send  ->  receive  ->  callback  (linked via topic_id & clock)

    Args:
        all_spans: Flat list of span records (unified schema).
        metadata_lookup: entity_id -> metadata dict.
        tracer: An OpenTelemetry Tracer instance.
    """
    # Pre-enrich all spans with metadata (adds _meta, _topic_name, _direction)
    enrich_spans(all_spans, metadata_lookup)

    # Classify spans by direction (from metadata) and op_type
    publisher_data = [s for s in all_spans if s['_direction'] == 'publisher']
    subscriber_data = [s for s in all_spans if s['_direction'] == 'subscriber']

    send_spans = [p for p in publisher_data if p.get('op_type') == OP_SEND]
    shm_handshake_spans = [p for p in publisher_data if p.get('op_type') == OP_SHM_HANDSHAKE]

    # Map publisher spans by (entity_id, clock) for context propagation
    publisher_span_contexts: Dict[tuple, Any] = {}

    # --- Publisher send spans (each clock tick starts a new trace) ---
    print("\n=== Creating Publisher Spans ===")
    for pub_data in send_spans:
        entity_id = pub_data['entity_id']
        clock = pub_data['clock']

        span_name = f"ecal.publish.{pub_data['_topic_name']}"
        span = tracer.start_span(span_name, start_time=pub_data['start_ns'])
        _set_common_attributes(span, pub_data, "send")

        publisher_span_contexts[(entity_id, clock)] = span.get_span_context()
        span.end(end_time=pub_data['end_ns'])

        print(f"Created publisher span: {span_name} [clock={clock}]")

    # --- SHM handshake spans (children of send at same entity_id & clock) ---
    print("\n=== Creating SHM Handshake Spans ===")
    for hs_data in shm_handshake_spans:
        entity_id = hs_data['entity_id']
        clock = hs_data['clock']

        span_name = f"ecal.shm_handshake.{hs_data['_topic_name']}"

        parent_key = (entity_id, clock)
        parent_ctx = None
        if parent_key in publisher_span_contexts:
            parent_ctx = trace.set_span_in_context(
                trace.NonRecordingSpan(publisher_span_contexts[parent_key])
            )

        span = tracer.start_span(span_name, context=parent_ctx,
                                 start_time=hs_data['start_ns'])
        _set_common_attributes(span, hs_data, "shm_handshake")
        span.end(end_time=hs_data['end_ns'])

        matched = parent_key in publisher_span_contexts
        print(f"Created shm_handshake span: {span_name} [clock={clock}]" +
              (f" -> child of send [clock={clock}]" if matched else " (no matching send)"))

    # --- Subscriber spans grouped by (topic_id, clock) ---
    sub_groups = defaultdict(lambda: {OP_RECEIVE: [], OP_CALLBACK: []})
    for sub_data in subscriber_data:
        topic_id = sub_data.get('topic_id')
        clock = sub_data['clock']
        op_type = sub_data.get('op_type', OP_RECEIVE)
        sub_groups[(topic_id, clock)][op_type].append(sub_data)

    receive_span_contexts: Dict[tuple, Any] = {}

    print("\n=== Creating Subscriber Spans ===")
    for (topic_id, clock), spans_by_type in sorted(sub_groups.items(),
                                                    key=lambda x: x[0][1]):
        # Look up matching publisher span via topic_id == publisher entity_id
        parent_key = (topic_id, clock)
        pub_ctx = None
        if parent_key in publisher_span_contexts:
            pub_ctx = trace.set_span_in_context(
                trace.NonRecordingSpan(publisher_span_contexts[parent_key])
            )

        # Receive spans — children of publisher send
        for sub_data in spans_by_type[OP_RECEIVE]:
            entity_id = sub_data['entity_id']
            span_name = f"ecal.receive.{sub_data['_topic_name']}"
            span = tracer.start_span(span_name, context=pub_ctx,
                                     start_time=sub_data['start_ns'])
            _set_common_attributes(span, sub_data, "receive")

            receive_span_contexts[(topic_id, clock, entity_id)] = span.get_span_context()
            span.end(end_time=sub_data['end_ns'])

            matched = parent_key in publisher_span_contexts
            print(f"Created receive span: {span_name} [clock={clock}]" +
                  (f" -> child of publisher" if matched else " (no matching publisher)"))

        # Callback spans — children of receive
        for sub_data in spans_by_type[OP_CALLBACK]:
            entity_id = sub_data['entity_id']
            span_name = f"ecal.callback.{sub_data['_topic_name']}"

            recv_key = (topic_id, clock, entity_id)
            recv_ctx = None
            if recv_key in receive_span_contexts:
                recv_ctx = trace.set_span_in_context(
                    trace.NonRecordingSpan(receive_span_contexts[recv_key])
                )

            span = tracer.start_span(span_name, context=recv_ctx,
                                     start_time=sub_data['start_ns'])
            _set_common_attributes(span, sub_data, "callback")
            span.end(end_time=sub_data['end_ns'])

            matched = recv_key in receive_span_contexts
            print(f"Created callback span: {span_name} [clock={clock}]" +
                  (f" -> child of receive" if matched else " (no matching receive)"))
