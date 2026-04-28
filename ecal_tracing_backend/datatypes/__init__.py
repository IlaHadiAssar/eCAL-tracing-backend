from typing import Union

from .ecal_enums import OperationType, TracingLayerType
from .publisher_span_data import SPublisherSpanData
from .subscriber_span_data import SSubscriberSpanData
from .topic_metadata import STopicMetadata

SpanData = Union[SPublisherSpanData, SSubscriberSpanData]
