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
* Implementing Instrumentation into User API
* Implementing Instrumentation into protocol headers (SHM,UDP,TCP)
+ Implementing Instrumentation into eCAL API (internal send, receive, callback ... functions)

## Decision Outcome

Chosen option: "Implementing Instrumentation into eCAL API", because this is the only option which doesnt: add dependencies (OpenTelemetry), change fundamantal functionality (protocol headers) or leave implementation for eCAL users.

### Consequences

* Good, because it enables tracing eCAL communication
* Bad, because it requires defining an eCAL specific trace format, which won't be compatible with common tracing frontend's

### Confirmation



## Pros and Cons of the Options

### Implementing Instrumentation into eCAL API

* Good, because it doesn't touch communication protocols
* Good, because it doesn't add external dependencies
* Good, because it doesn't require implementation in user projects
* Bad, because it requires defining an eCAL specific trace format, which won't be compatible with common tracing frontend's

## More Information
