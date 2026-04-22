"""Entry point for the eCAL tracing backend."""

from .parser import detect_parser
from .mapping import SpanMapper
from .exporting import export, OTLP_ENDPOINT


def main():
    # parse -> map -> export
    parser = detect_parser()
    spans = parser.load_spans()
    metadata = parser.load_metadata()

    mapper = SpanMapper(spans, metadata)
    tracer_providers = mapper.map_and_process(
        otlp_endpoint=OTLP_ENDPOINT,
    )

    export(tracer_providers)


if __name__ == "__main__":
    main()
