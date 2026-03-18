# 7. Tracing context propagation

Date: 2026-03-18

## Status

Accepted

## Context and Problem Statement
With context propagation, signals (traces) can be correlated with each other, regardless of where they are generated. Although not limited to tracing, context propagation allows traces to build causal information about a system across services that are arbitrarily distributed across process and network boundaries.

## Considered Options

* OpenTelemtry
    - ✅ ready to use
    - ✅ widely supported format for frontends
* Selfmade
    - ✅ removes external dependencies
    - ❌ implementation takes time
    - ❌ needs to be tailored to specific frontend

## Decision Outcome

Chosen option: "OpenTelemtry", because most simply implementation and widely accepted format.

### Consequences

* Good, because resulting traces are supported by many frontends and it saves lots of time

### Confirmation

## More Information
