from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from typing import Dict, List, Tuple

from .datatypes import SpanData


OTLP_ENDPOINT = "http://localhost:4318/v1/traces"


def setup_tracer_provider(otlp_endpoint: str = OTLP_ENDPOINT,
                          service_name: str = "ecal-tracing") -> tuple:

    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
    })

    tracer_provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    tracer = tracer_provider.get_tracer(__name__)

    return tracer_provider, tracer


def create_tracer_groups(
    spans_by_topic: Dict[str, List[SpanData]],
) -> List[Tuple]:
    tracer_groups = []
    for topic_name, topic_spans in sorted(spans_by_topic.items()):
        tracer_provider, tracer = setup_tracer_provider(
            service_name=topic_name,
        )
        tracer_groups.append((tracer_provider, tracer, topic_spans))

    return tracer_groups


def export(tracer_providers: list) -> None:
    for tp in tracer_providers:
        tp.shutdown()
    print("Export completed")

