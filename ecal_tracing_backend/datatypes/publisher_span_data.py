from dataclasses import dataclass


@dataclass
class SPublisherSpanData:
    op_type: int           # operation_type enum value
    entity_id: int         # uint64
    process_id: int        # uint64
    payload_size: int      # size_t
    clock: int             # long long
    layer: int             # uint64  (bitmask)
    start_ns: int          # start timestamp in nanoseconds
    end_ns: int            # end timestamp in nanoseconds
