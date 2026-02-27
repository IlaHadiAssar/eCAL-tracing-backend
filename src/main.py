from pathlib import Path

from mapping import load_json_file, build_metadata_lookup, create_spans_from_data
from exporting import setup_tracer_provider


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

    # Find all JSONL files in data directory
    json_files = sorted(data_dir.glob("*.jsonl"))

    if not json_files:
        print(f"Error: No JSONL files found in {data_dir}")
        return

    print(f"Found {len(json_files)} JSONL files\n")

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

    # Create and export spans
    tracer_provider, tracer = setup_tracer_provider()
    create_spans_from_data(publisher_data, subscriber_data, metadata_lookup, tracer)

    # Shutdown to ensure all spans are flushed to Jaeger
    tracer_provider.force_flush()
    tracer_provider.shutdown()
    print("\n=== Span creation complete ===")


if __name__ == "__main__":
    main()
