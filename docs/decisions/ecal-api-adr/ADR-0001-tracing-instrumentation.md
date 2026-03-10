---
status: accepted
date: 03.03.2026
decision-makers: Ila Hadi-Assar
consulted: Kerstin Keller, Kristof Hannemann
informed: eCAL Team
---

# Implement tracing Instrumentation in eCAL's API

## Context and Problem Statement
For a system to be observable, it must be instrumented: that is, code from the system’s components must emit signals, such as traces, metrics, and logs.


## Considered Options

* Implementing OpenTelemetry's Instrumentation API
    - :heavy_check_mark: ready to use
    - :x: adds external dependencies
* Implementing Instrumentation into User API
    - :heavy_check_mark: simple implementation on eCAL side
    - :x: not compatible with existing projects
* Implementing Instrumentation into protocol headers (SHM,UDP,TCP)
    - :heavy_check_mark: common approach
    - :x: might lead to issues with existing eCAL projects
+ Implementing Instrumentation into eCAL API (internal send, receive, callback ... functions)
    - :heavy_check_mark: doesn't touch communication protocols
    - :heavy_check_mark: doesn't add external dependencies
    - :heavy_check_mark: doesn't require implementation in user projects
    - :bad: slightly more complicated implementation

## Decision Outcome

Chosen option: "Implementing Instrumentation into eCAL API", because this is the only option which doesnt: add dependencies (OpenTelemetry), change fundamantal functionality (protocol headers) or leave implementation for eCAL users.

### Consequences

* Good, because it enables tracing eCAL communication
* Bad, because it requires defining an eCAL specific trace format, which needs to be mapped for compatibillity with common tracing frontend's

### Confirmation


## More Information
