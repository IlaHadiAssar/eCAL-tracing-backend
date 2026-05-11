from collections import defaultdict
from typing import Dict, List, NamedTuple, NewType

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.trace import SpanContext, Tracer

from .datatypes import (
    OperationType,
    SpanData,
    SPublisherSpanData,
    SSubscriberSpanData,
    STopicMetadata,
)
from .context_enrichment import ContextEnrichment


TopicEntityId = NewType("TopicEntityId", int)
SubscriberEntityId = NewType("SubscriberEntityId", int)
Clock = NewType("Clock", int)


class TopicClockKey(NamedTuple):
    topic_entity_id: TopicEntityId
    clock: Clock


class SubscriberReceiveKey(NamedTuple):
    topic_entity_id: TopicEntityId
    clock: Clock
    subscriber_entity_id: SubscriberEntityId


PublisherSpanIndex = Dict[TopicClockKey, SpanContext]
SubscriberReceiveSpanIndex = Dict[SubscriberReceiveKey, SpanContext]


class _PubSubSpanBuilder:

    def __init__(self, enricher: ContextEnrichment):
        self._enricher = enricher

    @staticmethod
    def _publisher_lookup_key(raw_span: SPublisherSpanData) -> TopicClockKey:
        return TopicClockKey(
            topic_entity_id=TopicEntityId(raw_span.entity_id),
            clock=Clock(raw_span.clock),
        )

    @staticmethod
    def _publisher_lookup_key_from_subscriber(raw_span: SSubscriberSpanData) -> TopicClockKey:
        return TopicClockKey(
            topic_entity_id=TopicEntityId(raw_span.topic_id),
            clock=Clock(raw_span.clock),
        )

    @staticmethod
    def _receive_lookup_key(raw_span: SSubscriberSpanData) -> SubscriberReceiveKey:
        return SubscriberReceiveKey(
            topic_entity_id=TopicEntityId(raw_span.topic_id),
            clock=Clock(raw_span.clock),
            subscriber_entity_id=SubscriberEntityId(raw_span.entity_id),
        )

    @staticmethod
    def _parent_context(span_context: SpanContext | None) -> Context | None:
        if span_context is None:
            return None
        return trace.set_span_in_context(trace.NonRecordingSpan(span_context))

    def _create_publisher_send(
        self,
        raw_span: SPublisherSpanData,
        tracer: Tracer,
        publisher_spans: PublisherSpanIndex,
    ) -> None:
        otel_span = tracer.start_span("send", start_time=raw_span.start_ns)
        self._enricher.set_attributes(otel_span, raw_span)
        lookup_key = self._publisher_lookup_key(raw_span)
        publisher_spans[lookup_key] = otel_span.get_span_context()
        otel_span.end(end_time=raw_span.end_ns)

    def _create_subscriber_receive(
        self,
        raw_span: SSubscriberSpanData,
        tracer: Tracer,
        publisher_spans: PublisherSpanIndex,
        subscriber_receive_spans: SubscriberReceiveSpanIndex,
    ) -> None:
        publisher_lookup_key = self._publisher_lookup_key_from_subscriber(raw_span)
        publisher_span_context = publisher_spans.get(publisher_lookup_key)
        otel_span = tracer.start_span(
            "receive",
            context=self._parent_context(publisher_span_context),
            start_time=raw_span.start_ns
        )
        self._enricher.set_attributes(otel_span, raw_span)
        receive_lookup_key = self._receive_lookup_key(raw_span)
        subscriber_receive_spans[receive_lookup_key] = otel_span.get_span_context()
        otel_span.end(end_time=raw_span.end_ns)

    def _create_callback_execution(
        self,
        raw_span: SSubscriberSpanData,
        tracer: Tracer,
        subscriber_receive_spans: SubscriberReceiveSpanIndex,
    ) -> None:
        receive_lookup_key = self._receive_lookup_key(raw_span)
        receive_span_context = subscriber_receive_spans.get(receive_lookup_key)
        otel_span = tracer.start_span(
            "callback",
            context=self._parent_context(receive_span_context),
            start_time=raw_span.start_ns
        )
        self._enricher.set_attributes(otel_span, raw_span)
        otel_span.end(end_time=raw_span.end_ns)

    def create_pub_sub_spans(
        self,
        topic_spans: List[SpanData],
        tracer: Tracer,
    ) -> None:
        """Build complete pub-sub trace chain: publisher sends -> subscriber receives -> callbacks."""
        publisher_spans: PublisherSpanIndex = {}
        for raw_span in topic_spans:
            if isinstance(raw_span, SPublisherSpanData):
                self._create_publisher_send(raw_span, tracer, publisher_spans)

        subscriber_receive_spans: SubscriberReceiveSpanIndex = {}
        for raw_span in topic_spans:
            if not isinstance(raw_span, SSubscriberSpanData):
                continue
            if raw_span.op_type == OperationType.RECEIVE:
                self._create_subscriber_receive(
                    raw_span, tracer, publisher_spans, subscriber_receive_spans,
                )

        for raw_span in topic_spans:
            if not isinstance(raw_span, SSubscriberSpanData):
                continue
            if raw_span.op_type == OperationType.CALLBACK_EXECUTION:
                self._create_callback_execution(raw_span, tracer, subscriber_receive_spans)


class ContextPropagator:
    """Transforms raw span data into linked OpenTelemetry traces."""

    def __init__(self, all_spans: List[SpanData], all_metadata: List[STopicMetadata]):
        self._all_spans = all_spans
        self._all_metadata = all_metadata
        self._enricher = ContextEnrichment(all_metadata)

    def group_spans_by_topic(self) -> Dict[str, List[SpanData]]:
        metadata_lookup = {meta.entity_id: meta for meta in self._all_metadata}
        spans_by_topic: Dict[str, List[SpanData]] = defaultdict(list)
        for span in self._all_spans:
            metadata = metadata_lookup.get(span.entity_id)
            topic_name = metadata.topic_name if metadata else str(span.entity_id)
            spans_by_topic[topic_name].append(span)
        return spans_by_topic

    def propagate(self, topic_spans: List[SpanData], tracer: Tracer) -> None:
        builder = _PubSubSpanBuilder(self._enricher)
        builder.create_pub_sub_spans(topic_spans, tracer)
