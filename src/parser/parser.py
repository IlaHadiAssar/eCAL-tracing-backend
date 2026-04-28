import glob
import os
from abc import ABC, abstractmethod
from typing import List

from ..datatypes import SpanData, STopicMetadata

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
SUPPORTED_TRACING_VERSIONS = {"1.0.0"}


class Parser(ABC):

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
        files = sorted(glob.glob(os.path.join(DATA_DIR, f"{prefix}*{self.file_extension}")))
        if not files:
            raise FileNotFoundError(f"No {prefix} files found in {DATA_DIR}")
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
