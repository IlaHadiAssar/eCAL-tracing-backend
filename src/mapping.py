from collections import defaultdict
from opentelemetry import trace
from typing import Any, Dict, List, Optional

from .datatypes import (
    OperationType,
    TracingLayerType,
    SpanData,
    SPublisherSpanData,
    SSubscriberSpanData,
    STopicMetadata,
)
from .exporting import setup_tracer_provider


class SpanMapper:

    def __init__(self, all_spans: List[SpanData], all_metadata: List[STopicMetadata]):
        self._all_spans = all_spans
        self._metadata_lookup = {meta.entity_id: meta for meta in all_metadata}

    def _get_tracing_version(self) -> str:
        for meta in self._metadata_lookup.values():
            if meta.tracing_version:
                return meta.tracing_version
        return "unknown"


    @staticmethod
    def _set_meta_attributes(span, meta: STopicMetadata) -> None:
        span.set_attribute("ecal.topic_name", meta.topic_name)
        span.set_attribute("ecal.type_name", meta.type_name)
        span.set_attribute("ecal.encoding", meta.encoding)
        span.set_attribute("ecal.host_name", meta.host_name)
        span.set_attribute("ecal.direction", meta.direction)
        span.set_attribute("ecal.tracing_version", meta.tracing_version)

    @classmethod
    def _set_publisher_attributes(cls, span, data: SPublisherSpanData,
                                  meta: Optional[STopicMetadata]) -> None:
        span.set_attribute("ecal.entity_id", data.entity_id)
        span.set_attribute("ecal.layer", TracingLayerType(data.layer).name.lower())
        span.set_attribute("ecal.layer_raw", data.layer)
        span.set_attribute("ecal.process_id", data.process_id)
        span.set_attribute("ecal.payload_size", data.payload_size)
        span.set_attribute("ecal.clock", data.clock)
        span.set_attribute("ecal.op_type", OperationType(data.op_type).name.lower())
        if meta is not None:
            cls._set_meta_attributes(span, meta)

    @classmethod
    def _set_subscriber_attributes(cls, span, data: SSubscriberSpanData,
                                    meta: Optional[STopicMetadata]) -> None:
        span.set_attribute("ecal.entity_id", data.entity_id)
        span.set_attribute("ecal.topic_id", data.topic_id)
        span.set_attribute("ecal.layer", TracingLayerType(data.layer).name.lower())
        span.set_attribute("ecal.layer_raw", data.layer)
        span.set_attribute("ecal.process_id", data.process_id)
        span.set_attribute("ecal.payload_size", data.payload_size)
        span.set_attribute("ecal.clock", data.clock)
        span.set_attribute("ecal.op_type", OperationType(data.op_type).name.lower())
        if meta is not None:
            cls._set_meta_attributes(span, meta)


# ---------------------------------------------------------------------------
# Span creation per operation type
# ---------------------------------------------------------------------------

    def _create_send_spans(
        self,
        send_spans: List[SPublisherSpanData],
        tracer,
    ) -> Dict[tuple, Any]:

        publisher_span_contexts: Dict[tuple, Any] = {}

        for data in send_spans:
            meta = self._metadata_lookup.get(data.entity_id)

            span = tracer.start_span("send", start_time=data.start_ns)
            self._set_publisher_attributes(span, data, meta)

            publisher_span_contexts[(data.entity_id, data.clock)] = span.get_span_context()
            span.end(end_time=data.end_ns)

        return publisher_span_contexts

    def _create_receive_spans(
        self,
        receive_spans: List[SSubscriberSpanData],
        tracer,
        publisher_span_contexts: Dict[tuple, Any],
    ) -> Dict[tuple, Any]:
        receive_span_contexts: Dict[tuple, Any] = {}

        for data in receive_spans:
            meta = self._metadata_lookup.get(data.entity_id)

            parent_key = (data.topic_id, data.clock)
            pub_ctx = None
            if parent_key in publisher_span_contexts:
                pub_ctx = trace.set_span_in_context(
                    trace.NonRecordingSpan(publisher_span_contexts[parent_key])
                )

            span = tracer.start_span("receive", context=pub_ctx,
                                     start_time=data.start_ns)
            self._set_subscriber_attributes(span, data, meta)

            recv_key = (data.topic_id, data.clock, data.entity_id)
            receive_span_contexts[recv_key] = span.get_span_context()
            span.end(end_time=data.end_ns)

        return receive_span_contexts

    def _create_callback_spans(
        self,
        callback_spans: List[SSubscriberSpanData],
        tracer,
        receive_span_contexts: Dict[tuple, Any],
    ) -> None:

        for data in callback_spans:
            meta = self._metadata_lookup.get(data.entity_id)

            recv_key = (data.topic_id, data.clock, data.entity_id)
            recv_ctx = None
            if recv_key in receive_span_contexts:
                recv_ctx = trace.set_span_in_context(
                    trace.NonRecordingSpan(receive_span_contexts[recv_key])
                )

            span = tracer.start_span("callback", context=recv_ctx,
                                     start_time=data.start_ns)
            self._set_subscriber_attributes(span, data, meta)
            span.end(end_time=data.end_ns)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

    def _create_spans_from_data(self, spans: List[SpanData], tracer) -> None:
        send_spans = [s for s in spans if s.op_type == OperationType.SEND]
        receive_spans = [s for s in spans if s.op_type == OperationType.RECEIVE]
        callback_spans = [s for s in spans if s.op_type == OperationType.CALLBACK_EXECUTION]

        publisher_span_contexts = self._create_send_spans(send_spans, tracer)

        receive_span_contexts = self._create_receive_spans(
            receive_spans, tracer, publisher_span_contexts,
        )

        self._create_callback_spans(callback_spans, tracer, receive_span_contexts)

    def map_and_process(self, otlp_endpoint: str) -> List:
        tracing_version = self._get_tracing_version()

        spans_by_topic: Dict[str, List[SpanData]] = defaultdict(list)
        for span in self._all_spans:
            meta = self._metadata_lookup.get(span.entity_id)
            topic_name = meta.topic_name if meta else str(span.entity_id)
            spans_by_topic[topic_name].append(span)

        print("Mapping...")
        tracer_providers = []
        for topic_name, topic_spans in sorted(spans_by_topic.items()):
            tracer_provider, tracer = setup_tracer_provider(
                otlp_endpoint=otlp_endpoint,
                tracing_version=tracing_version,
                service_name=topic_name,
            )
            tracer_providers.append(tracer_provider)
            self._create_spans_from_data(topic_spans, tracer)

        return tracer_providers
