import glob
import os
from abc import ABC, abstractmethod
from typing import List

from ..datatypes import SpanData, STopicMetadata

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))


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
        return all_metadata
