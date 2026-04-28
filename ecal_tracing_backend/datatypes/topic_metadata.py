from dataclasses import dataclass


@dataclass
class STopicMetadata:
    tracing_version: str   # tracing format version
    entity_id: int         # uint64
    process_id: int        # int32
    host_name: str         # host that created the topic
    topic_name: str        # topic name used for pub/sub matching
    encoding: str          # datatype encoding (e.g. protobuf)
    type_name: str         # datatype name
    direction: str         # "publisher" or "subscriber"
