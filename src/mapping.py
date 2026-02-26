import json
from collections import defaultdict
from opentelemetry import trace
from typing import List, Dict, Any


# op_type enum mapping from C++
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


def load_json_file(filepath: str) -> List[Dict[str, Any]]:
    """Load JSON file with span data"""
    with open(filepath, 'r') as f:
        return json.load(f)


def build_metadata_lookup(metadata_list: List[Dict]) -> Dict[int, Dict[str, Any]]:
    """Build a lookup from entity_id to metadata attributes"""
    return {meta['entity_id']: meta for meta in metadata_list}


def set_meta_attributes(span, meta: Dict[str, Any]) -> None:
    """Set common eCAL metadata attributes on a span"""
    if meta:
        for key in ('topic_name', 'type_name', 'encoding', 'host_name', 'direction'):
            span.set_attribute(f"ecal.{key}", meta.get(key, ''))


def enrich_spans(spans: List[Dict], metadata_lookup: Dict[int, Dict[str, Any]],
                 id_key: str = 'entity_id') -> None:
    """Pre-merge metadata into each span record to avoid repeated lookups"""
    for span in spans:
        meta = metadata_lookup.get(span[id_key], {})
        span['_meta'] = meta
        span['_topic_name'] = meta.get('topic_name', str(span[id_key]))


def create_spans_from_data(publisher_data: List[Dict], subscriber_data: List[Dict],
                           metadata_lookup: Dict[int, Dict[str, Any]],
                           tracer) -> None:
    """Create OpenTelemetry spans from eCAL publisher and subscriber data.

    Args:
        publisher_data: List of publisher span records.
        subscriber_data: List of subscriber span records.
        metadata_lookup: entity_id -> metadata dict.
        tracer: An OpenTelemetry Tracer instance.
    """
    # Map publisher spans by (entity_id, clock) for context propagation
    publisher_span_contexts = {}
    publisher_end_times = {}

    # Pre-enrich all spans with metadata
    enrich_spans(publisher_data, metadata_lookup)
    enrich_spans(subscriber_data, metadata_lookup)

    # Separate publisher data into send and shm_handshake spans
    send_spans = [p for p in publisher_data if p.get('op_type') == OP_SEND]
    shm_handshake_spans = [p for p in publisher_data if p.get('op_type') == OP_SHM_HANDSHAKE]

    # Create publisher send spans — each clock tick gets its own trace
    print("\n=== Creating Publisher Spans ===")
    for pub_data in send_spans:
        entity_id = pub_data['entity_id']
        clock = pub_data['clock']
        start_ns = pub_data['start_ns']
        end_ns = pub_data['end_ns']

        topic_name = pub_data['_topic_name']
        span_name = f"ecal.publish.{topic_name}"

        # Each publish span starts a new trace (no shared parent)
        span = tracer.start_span(span_name, start_time=start_ns)

        span.set_attribute("ecal.entity_id", entity_id)
        span.set_attribute("ecal.layer", pub_data.get('layer'))
        span.set_attribute("ecal.process_id", pub_data.get('process_id'))
        span.set_attribute("ecal.payload_size", pub_data.get('payload_size'))
        span.set_attribute("ecal.clock", clock)
        span.set_attribute("ecal.op_type", "send")
        set_meta_attributes(span, pub_data['_meta'])

        # Store span context keyed by (entity_id, clock) for parent linking
        publisher_span_contexts[(entity_id, clock)] = span.get_span_context()
        publisher_end_times[(entity_id, clock)] = end_ns

        span.end(end_time=end_ns)

        print(f"Created publisher span: {span_name} [clock={clock}]")

    # Create shm_handshake spans as children of the corresponding send span
    print("\n=== Creating SHM Handshake Spans ===")
    for hs_data in shm_handshake_spans:
        entity_id = hs_data['entity_id']
        clock = hs_data['clock']
        start_ns = hs_data['start_ns']
        end_ns = hs_data['end_ns']

        topic_name = hs_data['_topic_name']
        span_name = f"ecal.shm_handshake.{topic_name}"

        # shm_handshake at clock C is a child of the send at clock C-1
        parent_key = (entity_id, clock - 1)
        parent_ctx = None
        if parent_key in publisher_span_contexts:
            parent_ctx = trace.set_span_in_context(
                trace.NonRecordingSpan(publisher_span_contexts[parent_key])
            )

        span = tracer.start_span(span_name, context=parent_ctx, start_time=start_ns)

        span.set_attribute("ecal.entity_id", entity_id)
        span.set_attribute("ecal.layer", hs_data.get('layer'))
        span.set_attribute("ecal.process_id", hs_data.get('process_id'))
        span.set_attribute("ecal.payload_size", hs_data.get('payload_size'))
        span.set_attribute("ecal.clock", clock)
        span.set_attribute("ecal.op_type", "shm_handshake")
        set_meta_attributes(span, hs_data['_meta'])

        span.end(end_time=end_ns)

        matched = parent_key in publisher_span_contexts
        print(f"Created shm_handshake span: {span_name} [clock={clock}]" +
              (f" -> child of send [clock={clock - 1}]" if matched else " (no matching send)"))

    # Group subscriber spans by (topic_id, clock) and op_type
    # For each message: publish -> receive -> callback
    sub_groups = defaultdict(lambda: {OP_RECEIVE: [], OP_CALLBACK: []})
    for sub_data in subscriber_data:
        topic_id = sub_data.get('topic_id')
        clock = sub_data['clock']
        op_type = sub_data.get('op_type', OP_RECEIVE)
        sub_groups[(topic_id, clock)][op_type].append(sub_data)

    # Track receive span contexts for callback parenting
    receive_span_contexts = {}

    print("\n=== Creating Subscriber Spans ===")
    for (topic_id, clock), spans_by_type in sorted(sub_groups.items(), key=lambda x: x[0][1]):
        # Look up matching publisher span (clock - 1 offset)
        parent_key = (topic_id, clock - 1)
        pub_ctx = None
        if parent_key in publisher_span_contexts:
            pub_ctx = trace.set_span_in_context(
                trace.NonRecordingSpan(publisher_span_contexts[parent_key])
            )

        # Create receive spans as children of publisher
        for sub_data in spans_by_type[OP_RECEIVE]:
            entity_id = sub_data['entity_id']
            sub_topic_name = sub_data['_topic_name']

            # Create receive span as child of publisher span
            span_name = f"ecal.receive.{sub_topic_name}"
            span = tracer.start_span(span_name, context=pub_ctx, start_time=sub_data['start_ns'])

            span.set_attribute("ecal.entity_id", entity_id)
            span.set_attribute("ecal.layer", sub_data.get('layer'))
            span.set_attribute("ecal.process_id", sub_data.get('process_id'))
            span.set_attribute("ecal.topic_id", topic_id)
            span.set_attribute("ecal.clock", clock)
            span.set_attribute("ecal.op_type", "receive")
            set_meta_attributes(span, sub_data['_meta'])

            # Store for callback parenting
            receive_span_contexts[(topic_id, clock, entity_id)] = span.get_span_context()

            span.end(end_time=sub_data['end_ns'])

            matched = parent_key in publisher_span_contexts
            print(f"Created receive span: {span_name} [clock={clock}]" +
                  (f" -> child of publisher" if matched else " (no matching publisher)"))

        # Create callback spans as children of receive
        for sub_data in spans_by_type[OP_CALLBACK]:
            entity_id = sub_data['entity_id']
            cb_topic_name = sub_data['_topic_name']
            span_name = f"ecal.callback.{cb_topic_name}"

            recv_key = (topic_id, clock, entity_id)
            recv_ctx = None
            if recv_key in receive_span_contexts:
                recv_ctx = trace.set_span_in_context(
                    trace.NonRecordingSpan(receive_span_contexts[recv_key])
                )

            span = tracer.start_span(span_name, context=recv_ctx, start_time=sub_data['start_ns'])

            span.set_attribute("ecal.entity_id", entity_id)
            span.set_attribute("ecal.layer", sub_data.get('layer'))
            span.set_attribute("ecal.process_id", sub_data.get('process_id'))
            span.set_attribute("ecal.topic_id", topic_id)
            span.set_attribute("ecal.clock", clock)
            span.set_attribute("ecal.op_type", "callback")
            set_meta_attributes(span, sub_data['_meta'])

            span.end(end_time=sub_data['end_ns'])

            matched = recv_key in receive_span_contexts
            print(f"Created callback span: {span_name} [clock={clock}]" +
                  (f" -> child of receive" if matched else " (no matching receive)"))
