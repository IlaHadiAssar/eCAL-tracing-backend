"""Entry point for the eCAL tracing backend.

Loads all span and metadata JSONL files from a data directory, builds the
unified OpenTelemetry trace hierarchy, and exports to Jaeger via OTLP.
"""

import argparse
import glob
import os

from .mapping import (
    load_json_file,
    build_metadata_lookup,
    get_tracing_version,
    create_spans_from_data,
)
from .exporting import setup_tracer_provider


def collect_files(data_dir: str):
    """Discover span and metadata JSONL files in *data_dir*.

    Returns:
        (span_files, metadata_files) – two sorted lists of absolute paths.
    """
    span_files = sorted(glob.glob(os.path.join(data_dir, "ecal_spans_*.jsonl")))
    meta_files = sorted(glob.glob(os.path.join(data_dir, "ecal_topic_metadata_*.jsonl")))
    return span_files, meta_files


def main():
    parser = argparse.ArgumentParser(description="eCAL → OpenTelemetry trace exporter")
    parser.add_argument(
        "--otlp-endpoint",
        default="http://localhost:4318/v1/traces",
        help="OTLP HTTP endpoint (default: %(default)s)",
    )
    args = parser.parse_args()

    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    span_files, meta_files = collect_files(data_dir)

    if not span_files:
        print(f"No span files found in {data_dir}")
        return
    if not meta_files:
        print(f"No metadata files found in {data_dir}")
        return

    # --- Load metadata -------------------------------------------------------
    all_metadata: list = []
    for mf in meta_files:
        print(f"Loading metadata: {mf}")
        all_metadata.extend(load_json_file(mf))

    metadata_lookup = build_metadata_lookup(all_metadata)
    tracing_version = get_tracing_version(metadata_lookup)
    print(f"Detected eCAL tracing version: {tracing_version}")

    # --- Load spans (unified schema) -----------------------------------------
    all_spans: list = []
    for sf in span_files:
        print(f"Loading spans: {sf}")
        all_spans.extend(load_json_file(sf))

    print(f"Loaded {len(all_spans)} spans from {len(span_files)} file(s)")

    # --- Set up OTel pipeline -------------------------------------------------
    tracer_provider, tracer = setup_tracer_provider(
        otlp_endpoint=args.otlp_endpoint,
        tracing_version=tracing_version,
    )

    # --- Create & export spans ------------------------------------------------
    create_spans_from_data(all_spans, metadata_lookup, tracer)

    tracer_provider.shutdown()
    print("\nDone – spans exported.")


if __name__ == "__main__":
    main()
