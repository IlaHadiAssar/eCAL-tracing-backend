import json
from typing import List

from ..datatypes import (
    SpanData,
    OperationType,
    SPublisherSpanData,
    SSubscriberSpanData,
    STopicMetadata,
)
from . import Parser


class ParserJsonl(Parser):

    @property
    def file_extension(self) -> str:
        return ".jsonl"

    def _parse_span_line(self, data: dict) -> SpanData:
        if data["op_type"] == OperationType.SEND:
            return SPublisherSpanData(
                op_type=data["op_type"],
                entity_id=data["entity_id"],
                process_id=data["process_id"],
                payload_size=data["payload_size"],
                clock=data["clock"],
                layer=data["layer"],
                start_ns=data["start_ns"],
                end_ns=data["end_ns"],
            )
        return SSubscriberSpanData(
            op_type=data["op_type"],
            entity_id=data["entity_id"],
            topic_id=data["topic_id"],
            process_id=data["process_id"],
            payload_size=data["payload_size"],
            clock=data["clock"],
            layer=data["layer"],
            start_ns=data["start_ns"],
            end_ns=data["end_ns"],
        )

    def _parse_metadata_line(self, data: dict) -> STopicMetadata:
        return STopicMetadata(
            tracing_version=data["tracing_version"],
            entity_id=data["entity_id"],
            process_id=data["process_id"],
            host_name=data["host_name"],
            topic_name=data["topic_name"],
            encoding=data["encoding"],
            type_name=data["type_name"],
            direction=data["direction"],
        )

    def parse_span_file(self, filepath: str) -> List[SpanData]:
        spans: List[SpanData] = []
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    spans.append(self._parse_span_line(data))
        return spans

    def parse_metadata_file(self, filepath: str) -> List[STopicMetadata]:
        metadata: List[STopicMetadata] = []
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    metadata.append(self._parse_metadata_line(data))
        return metadata
