from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource


OTLP_ENDPOINT = "http://localhost:4318/v1/traces"


def setup_tracer_provider(otlp_endpoint: str = OTLP_ENDPOINT,
                          tracing_version: str = "unknown",
                          service_name: str = "ecal-tracing") -> tuple:

    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
        "ecal.tracing_version": tracing_version,
    })

    tracer_provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    tracer = tracer_provider.get_tracer(__name__)

    return tracer_provider, tracer


def export(tracer_providers: list) -> None:
    for tp in tracer_providers:
        tp.shutdown()
    print("Export completed")

