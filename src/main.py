import json
from datetime import datetime
from pathlib import Path
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.trace import SpanContext, TraceFlags, Link, TraceState
from opentelemetry.sdk.resources import Resource
from typing import List, Dict, Any
import time


class ConsoleSpanExporter(SpanExporter):
    """Simple exporter that prints spans to console"""

    def export(self, spans):
        for span in spans:
            print(f"Span: {span.name} | Start: {span.start_time} | End: {span.end_time} | Duration: {span.end_time - span.start_time}ns")
            if span.links:
                for link in span.links:
                    print(f"  -> Linked to trace: {link.context.trace_id}")
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


def load_json_file(filepath: str) -> List[Dict[str, Any]]:
    """Load JSON file with span data"""
    with open(filepath, 'r') as f:
        return json.load(f)


def build_metadata_lookup(metadata_list: List[Dict]) -> Dict[int, Dict[str, Any]]:
    """Build a lookup from entity_id to metadata attributes"""
    lookup = {}
    for meta in metadata_list:
        lookup[meta['entity_id']] = meta
    return lookup


def create_spans_from_data(publisher_data: List[Dict], subscriber_data: List[Dict],
                           metadata_lookup: Dict[int, Dict[str, Any]]) -> None:
    """Create OpenTelemetry spans from eCAL publisher and subscriber data"""

    # Setup tracer provider with resource
    resource = Resource.create({
        "service.name": "ecal-tracing",
        "service.version": "1.0.0"
    })

    tracer_provider = TracerProvider(resource=resource)

    # Add console exporter for debugging
    console_exporter = ConsoleSpanExporter()
    tracer_provider.add_span_processor(SimpleSpanProcessor(console_exporter))

    # Export to Jaeger via OTLP HTTP
    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(tracer_provider)
    tracer = trace.get_tracer(__name__)

    # op_type enum mapping from C++
    OP_SEND = 0
    OP_RECEIVE = 1
    OP_CALLBACK = 2

    # Map publisher spans by (entity_id, clock) for context propagation
    publisher_span_contexts = {}
    publisher_end_times = {}

    from collections import defaultdict

    # Create publisher spans — each clock tick gets its own trace
    print("\n=== Creating Publisher Spans ===")
    for pub_data in publisher_data:
        entity_id = pub_data['entity_id']
        clock = pub_data['clock']
        start_ns = pub_data['start_ns']
        end_ns = pub_data['end_ns']

        meta = metadata_lookup.get(entity_id, {})
        topic_name = meta.get('topic_name', str(entity_id))
        span_name = f"ecal.publish.{topic_name}"

        # Each publish span starts a new trace (no shared parent)
        span = tracer.start_span(span_name, start_time=start_ns)

        span.set_attribute("ecal.entity_id", entity_id)
        span.set_attribute("ecal.layer", pub_data.get('layer'))
        span.set_attribute("ecal.process_id", pub_data.get('process_id'))
        span.set_attribute("ecal.payload_size", pub_data.get('payload_size'))
        span.set_attribute("ecal.clock", clock)
        span.set_attribute("ecal.op_type", "send")
        # Add metadata attributes
        if meta:
            span.set_attribute("ecal.topic_name", meta.get('topic_name', ''))
            span.set_attribute("ecal.type_name", meta.get('type_name', ''))
            span.set_attribute("ecal.encoding", meta.get('encoding', ''))
            span.set_attribute("ecal.host_name", meta.get('host_name', ''))
            span.set_attribute("ecal.direction", meta.get('direction', ''))

        # Store span context keyed by (entity_id, clock) for parent linking
        publisher_span_contexts[(entity_id, clock)] = span.get_span_context()
        publisher_end_times[(entity_id, clock)] = end_ns

        span.end(end_time=end_ns)

        print(f"Created publisher span: {span_name} [clock={clock}]")

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

        # Create wait + receive spans; wait is child of publisher, receive is child of wait
        for sub_data in spans_by_type[OP_RECEIVE]:
            entity_id = sub_data['entity_id']
            meta = metadata_lookup.get(entity_id, {})
            sub_topic_name = meta.get('topic_name', str(entity_id))

            # Create wait span (from publish end to receive start)
            wait_ctx = pub_ctx  # fallback: wait is child of publisher
            if parent_key in publisher_span_contexts:
                pub_end_time = publisher_end_times[parent_key]
                wait_span_name = f"ecal.wait.{sub_topic_name}"
                wait_span = tracer.start_span(wait_span_name, context=pub_ctx, start_time=pub_end_time)
                wait_span.set_attribute("ecal.entity_id", entity_id)
                wait_span.set_attribute("ecal.topic_id", topic_id)
                wait_span.set_attribute("ecal.clock", clock)
                wait_span.set_attribute("ecal.op_type", "wait")
                # Add metadata attributes
                if meta:
                    wait_span.set_attribute("ecal.topic_name", meta.get('topic_name', ''))
                    wait_span.set_attribute("ecal.type_name", meta.get('type_name', ''))
                    wait_span.set_attribute("ecal.encoding", meta.get('encoding', ''))
                    wait_span.set_attribute("ecal.host_name", meta.get('host_name', ''))
                    wait_span.set_attribute("ecal.direction", meta.get('direction', ''))
                wait_span.end(end_time=sub_data['start_ns'])

                wait_ctx = trace.set_span_in_context(
                    trace.NonRecordingSpan(wait_span.get_span_context())
                )
                print(f"Created wait span: {wait_span_name} [clock={clock}] -> child of publisher {topic_id}")

            # Create receive span as child of wait span
            span_name = f"ecal.receive.{sub_topic_name}"
            span = tracer.start_span(span_name, context=wait_ctx, start_time=sub_data['start_ns'])

            span.set_attribute("ecal.entity_id", entity_id)
            span.set_attribute("ecal.layer", sub_data.get('layer'))
            span.set_attribute("ecal.process_id", sub_data.get('process_id'))
            span.set_attribute("ecal.topic_id", topic_id)
            span.set_attribute("ecal.clock", clock)
            span.set_attribute("ecal.op_type", "receive")
            # Add metadata attributes
            if meta:
                span.set_attribute("ecal.topic_name", meta.get('topic_name', ''))
                span.set_attribute("ecal.type_name", meta.get('type_name', ''))
                span.set_attribute("ecal.encoding", meta.get('encoding', ''))
                span.set_attribute("ecal.host_name", meta.get('host_name', ''))
                span.set_attribute("ecal.direction", meta.get('direction', ''))

            # Store for callback parenting
            receive_span_contexts[(topic_id, clock, entity_id)] = span.get_span_context()

            span.end(end_time=sub_data['end_ns'])

            matched = parent_key in publisher_span_contexts
            print(f"Created receive span: {span_name} [clock={clock}]" +
                  (f" -> child of wait span" if matched else " (no matching publisher)"))

        # Create callback spans as children of receive
        for sub_data in spans_by_type[OP_CALLBACK]:
            entity_id = sub_data['entity_id']
            meta = metadata_lookup.get(entity_id, {})
            cb_topic_name = meta.get('topic_name', str(entity_id))
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
            # Add metadata attributes
            if meta:
                span.set_attribute("ecal.topic_name", meta.get('topic_name', ''))
                span.set_attribute("ecal.type_name", meta.get('type_name', ''))
                span.set_attribute("ecal.encoding", meta.get('encoding', ''))
                span.set_attribute("ecal.host_name", meta.get('host_name', ''))
                span.set_attribute("ecal.direction", meta.get('direction', ''))

            span.end(end_time=sub_data['end_ns'])

            matched = recv_key in receive_span_contexts
            print(f"Created callback span: {span_name} [clock={clock}]" +
                  (f" -> child of receive" if matched else " (no matching receive)"))

    # Shutdown to ensure all spans are flushed to Jaeger
    tracer_provider.force_flush()
    tracer_provider.shutdown()
    print("\n=== Span creation complete ===")


def main():
    # Get paths relative to script location
    script_dir = Path(__file__).parent.parent
    data_dir = script_dir / "data"

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        return

    # Load all per-process span and metadata files
    publisher_data = []
    subscriber_data = []
    metadata_all = []

    # Find all JSON files in data directory
    json_files = sorted(data_dir.glob("*.json"))

    if not json_files:
        print(f"Error: No JSON files found in {data_dir}")
        return

    print(f"Found {len(json_files)} JSON files\n")

    # Load and categorize spans and metadata
    for json_file in json_files:
        print(f"Loading: {json_file.name}")
        data = load_json_file(str(json_file))

        if "topic_metadata" in json_file.name:
            metadata_all.extend(data)
            print(f"  Loaded {len(data)} metadata entries")
        elif "publisher" in json_file.name:
            publisher_data.extend(data)
            print(f"  Loaded {len(data)} publisher spans")
        elif "subscriber" in json_file.name:
            subscriber_data.extend(data)
            print(f"  Loaded {len(data)} subscriber spans")

    # Build metadata lookup by entity_id
    metadata_lookup = build_metadata_lookup(metadata_all)
    print(f"\nMetadata entries: {len(metadata_lookup)} entities")
    print(f"Total: {len(publisher_data)} publisher spans and {len(subscriber_data)} subscriber spans\n")

    # Create spans
    create_spans_from_data(publisher_data, subscriber_data, metadata_lookup)


if __name__ == "__main__":
    main()
