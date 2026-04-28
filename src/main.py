"""Entry point for the eCAL tracing backend."""

from .parser import detect_parser
from .context_propagator import ContextPropagator
from .exporting import create_tracer_groups, export


def main():
    # parse -> propagate -> export
    parser = detect_parser()
    spans = parser.load_spans()
    metadata = parser.load_metadata()

    propagator = ContextPropagator(spans, metadata)
    spans_by_topic = propagator.group_spans_by_topic()
    tracer_groups = create_tracer_groups(spans_by_topic)

    print("Mapping & propagating...")
    tracer_providers = []
    for tracer_provider, tracer, topic_spans in tracer_groups:
        propagator.propagate(topic_spans, tracer)
        tracer_providers.append(tracer_provider)

    export(tracer_providers)


if __name__ == "__main__":
    main()
