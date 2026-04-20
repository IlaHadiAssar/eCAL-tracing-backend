from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource


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


def setup_tracer_provider(otlp_endpoint: str = "http://localhost:4318/v1/traces",
                          tracing_version: str = "unknown") -> tuple:
    """Set up and return (tracer_provider, tracer) with console and OTLP exporters.

    Args:
        otlp_endpoint: OTLP HTTP endpoint URL.
        tracing_version: eCAL tracing schema version from metadata.
    """
    resource = Resource.create({
        "service.name": "ecal-tracing",
        "service.version": "1.0.0",
        "ecal.tracing_version": tracing_version,
    })

    tracer_provider = TracerProvider(resource=resource)

    # Add console exporter for debugging
    console_exporter = ConsoleSpanExporter()
    tracer_provider.add_span_processor(SimpleSpanProcessor(console_exporter))

    # Export to Jaeger via OTLP HTTP
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(tracer_provider)
    tracer = trace.get_tracer(__name__)

    return tracer_provider, tracer
