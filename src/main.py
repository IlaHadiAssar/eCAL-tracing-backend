"""Entry point for the eCAL tracing backend."""

import argparse
from typing import Sequence

from .parser import detect_parser
from .context_propagator import ContextPropagator
from .exporting import create_tracer_groups, export

DEFAULT_DATA_DIR = "~/.ecal/traces"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    cli_parser = argparse.ArgumentParser(description="Export eCAL tracing data to OpenTelemetry")
    cli_parser.add_argument(
        "--data-dir",
        default=DEFAULT_DATA_DIR,
        help="Directory containing eCAL tracing data files (default: %(default)s)",
    )
    return cli_parser.parse_args(argv)


def main(argv: Sequence[str] | None = None):
    args = parse_args(argv)

    # parse -> propagate -> export
    data_parser = detect_parser(args.data_dir)
    spans = data_parser.load_spans()
    metadata = data_parser.load_metadata()

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
