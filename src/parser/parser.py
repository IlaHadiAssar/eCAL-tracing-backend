import glob
import os
from abc import ABC, abstractmethod
from typing import List

from ..datatypes import SpanData, STopicMetadata

SUPPORTED_TRACING_VERSIONS = {"1.0.0"}


def resolve_data_dir(data_dir: str) -> str:
    return os.path.abspath(os.path.expanduser(data_dir))


class Parser(ABC):

    def __init__(self, data_dir: str) -> None:
        self.data_dir = resolve_data_dir(data_dir)

    @property
    @abstractmethod
    def file_extension(self) -> str:
        ...

    @abstractmethod
    def parse_span_file(self, filepath: str) -> List[SpanData]:
        ...

    @abstractmethod
    def parse_metadata_file(self, filepath: str) -> List[STopicMetadata]:
        ...

    def _collect_files(self, prefix: str) -> List[str]:
        files = sorted(glob.glob(os.path.join(self.data_dir, f"{prefix}*{self.file_extension}")))
        if not files:
            raise FileNotFoundError(f"No {prefix} files found in {self.data_dir}")
        return files

    def _validate_metadata_tracing_version(self, metadata: List[STopicMetadata]) -> None:
        versions = {
            meta.tracing_version.strip()
            for meta in metadata
            if meta.tracing_version and meta.tracing_version.strip()
        }

        if not versions:
            raise ValueError("No tracing_version found in metadata")

        if len(versions) > 1:
            sorted_versions = ", ".join(sorted(versions))
            raise ValueError(f"Mixed tracing_version values found: {sorted_versions}")

        version = next(iter(versions))
        if version not in SUPPORTED_TRACING_VERSIONS:
            supported = ", ".join(sorted(SUPPORTED_TRACING_VERSIONS))
            raise ValueError(
                f"Unsupported tracing_version '{version}'. Supported versions: {supported}"
            )

    def load_spans(self) -> List[SpanData]:
        span_files = self._collect_files("ecal_spans_")
        all_spans: List[SpanData] = []
        for sf in span_files:
            all_spans.extend(self.parse_span_file(sf))
        return all_spans

    def load_metadata(self) -> List[STopicMetadata]:
        meta_files = self._collect_files("ecal_topic_metadata_")
        all_metadata: List[STopicMetadata] = []
        for mf in meta_files:
            all_metadata.extend(self.parse_metadata_file(mf))
        self._validate_metadata_tracing_version(all_metadata)
        return all_metadata
