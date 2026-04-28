from typing import List

from .datatypes import (
    OperationType,
    TracingLayerType,
    SpanData,
    SPublisherSpanData,
    SSubscriberSpanData,
    STopicMetadata,
)


class ContextEnrichment:
    def __init__(self, metadata: List[STopicMetadata]):
        self._metadata_lookup = {meta.entity_id: meta for meta in metadata}

    @staticmethod
    def _set_meta_attributes(span, meta: STopicMetadata) -> None:
        span.set_attribute("topic_name", meta.topic_name)
        span.set_attribute("type_name", meta.type_name)
        span.set_attribute("encoding", meta.encoding)
        span.set_attribute("host_name", meta.host_name)
        span.set_attribute("direction", meta.direction)

    def set_publisher_attributes(self, span, data: SPublisherSpanData) -> None:
        meta = self._metadata_lookup.get(data.entity_id)
        span.set_attribute("entity_id", data.entity_id)
        span.set_attribute("layer", TracingLayerType(data.layer).name.lower())
        span.set_attribute("layer_raw", data.layer)
        span.set_attribute("process_id", data.process_id)
        span.set_attribute("payload_size", data.payload_size)
        span.set_attribute("clock", data.clock)
        span.set_attribute("op_type", OperationType(data.op_type).name.lower())
        if meta is not None:
            self._set_meta_attributes(span, meta)

    def set_subscriber_attributes(self, span, data: SSubscriberSpanData) -> None:
        meta = self._metadata_lookup.get(data.entity_id)
        span.set_attribute("entity_id", data.entity_id)
        span.set_attribute("topic_id", data.topic_id)
        span.set_attribute("layer", TracingLayerType(data.layer).name.lower())
        span.set_attribute("layer_raw", data.layer)
        span.set_attribute("process_id", data.process_id)
        span.set_attribute("payload_size", data.payload_size)
        span.set_attribute("clock", data.clock)
        span.set_attribute("op_type", OperationType(data.op_type).name.lower())
        if meta is not None:
            self._set_meta_attributes(span, meta)

    def set_attributes(self, span, data: SpanData) -> None:
        if isinstance(data, SPublisherSpanData):
            self.set_publisher_attributes(span, data)
            return

        if isinstance(data, SSubscriberSpanData):
            self.set_subscriber_attributes(span, data)
            return

        raise TypeError(f"Unsupported span data type: {type(data)!r}")
