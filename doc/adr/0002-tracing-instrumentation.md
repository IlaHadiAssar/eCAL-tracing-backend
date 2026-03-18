# 2. Tracing instrumentation

Date: 2026-03-03
decision-makers: Ila Hadi-Assar
consulted: Kerstin Keller, Kristof Hannemann
informed: eCAL Team

## Status

Accepted

## Context and Problem Statement
For a system to be observable, it must be instrumented: that is, code from the system’s components must emit signals, such as traces.


## Considered Options

* **Implementing OpenTelemetry's Instrumentation API**
    - ✅ ready to use
    - ❌ adds external dependencies
* **Implementing Instrumentation into User API**
    - ✅ simple implementation on eCAL side
    - ❌ not compatible with existing projects
* **Implementing Instrumentation into protocol headers** (SHM,UDP,TCP)
    - ✅  common approach
    - ❌ might lead to issues with existing eCAL projects
* **Implementing Instrumentation into eCAL API (internal send, receive, callback ... functions)**
    - ✅ doesn't touch communication protocols
    - ✅ doesn't add external dependencies
    - ✅ doesn't require implementation in user projects
    - ❌ slightly more complicated implementation

## Decision Outcome

Chosen option: "Implementing Instrumentation into eCAL API", because this is the only option which doesnt: add dependencies (OpenTelemetry), change fundamantal functionality (protocol headers) or leave implementation for eCAL users.

### Consequences

* Good, because it enables tracing eCAL communication
* Bad, because it adds overhead to eCAL communication

### Confirmation


## More Information
