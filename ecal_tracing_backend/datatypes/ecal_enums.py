# ---------------------------------------------------------------------------
# C++ enum mirrors  (namespace tracing)
# ---------------------------------------------------------------------------

from enum import IntEnum


# operation_type – specifies the type of operation being traced
class OperationType(IntEnum):
    SEND = 0
    RECEIVE = 1
    CALLBACK_EXECUTION = 2


# eTracingLayerType – active transport layer(s)
class TracingLayerType(IntEnum):
    NONE = 0
    SHM = 1
    UDP = 2
    SHM_UDP = 3
    TCP = 4
    SHM_TCP = 5
    UDP_TCP = 6
    ALL = 7
