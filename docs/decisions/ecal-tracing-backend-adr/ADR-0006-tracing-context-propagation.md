---
status:
date:
decision-makers:
consulted:
informed:
---

# Use OpenTelemetry library for context propagation

## Context and Problem Statement
With context propagation, signals (traces, metrics, and logs) can be correlated with each other, regardless of where they are generated. Although not limited to tracing, context propagation allows traces to build causal information about a system across services that are arbitrarily distributed across process and network boundaries.

## Considered Options

* OpenTelemtry
* Selfmade

## Decision Outcome

Chosen option: "OpenTelemtry", because most simply implementation and widely accepted format.

### Consequences

* Good, because resulting traces are supported by many frontends
* Good, because saves a lot of time

### Confirmation



## Pros and Cons of the Options

### OpenTelemtry

* Good, because resulting traces are supported by many frontends
* Good, because saves a lot of time

## More Information
