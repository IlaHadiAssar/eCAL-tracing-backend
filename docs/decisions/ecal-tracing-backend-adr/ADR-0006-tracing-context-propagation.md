---
status: accepted
date: 03.03.2026
decision-makers: Ila Hadi-Assar
consulted:
informed: eCAL Team
---

# Use OpenTelemetry library for context propagation

## Context and Problem Statement
With context propagation, signals (traces) can be correlated with each other, regardless of where they are generated. Although not limited to tracing, context propagation allows traces to build causal information about a system across services that are arbitrarily distributed across process and network boundaries.

## Considered Options

* OpenTelemtry
    - :heavy_check_mark: ready to use
    - :heavy_check_mark: widely supported format for frontends
* Selfmade
    - :heavy_check_mark: removes external dependencies
    - :x: implementation takes time
    - :x: needs to be tailored to specific frontend

## Decision Outcome

Chosen option: "OpenTelemtry", because most simply implementation and widely accepted format.

### Consequences

* Good, because resulting traces are supported by many frontends and it saves lots of time

### Confirmation

## More Information
