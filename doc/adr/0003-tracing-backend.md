# 3. Tracing backend

Date: 2026-03-17

## Status

Accepted

## Context and Problem Statement
Creating high amounts of Traces and uploading them to a frontend requires a lot of computation and adds external dependencies if you want Compliance with OpenTelemetry which is widely supported for tracing frontends

## Considered Options

* Implement custom solution inside eCAL with full tracing support
    - ✅ all-in-one solution results in most simple code
    - ❌ adds heavy load on eCAL
* Export minimal traces and handle logic on a tracing backend
    - ✅ moves most of the heavy load from eCAL to a seperate application
    - ✅ enables usage of external dependencies
    - ❌ overall more computation required
    - ❌ traces need to be mapped on the backend

## Decision Outcome

Chosen option: "Export minimal traces and handle logic on a tracing backend"
### Consequences

* Good, because overhead in eCAL is kept to a minimum
* Bad, because another repository has to be maintained

### Confirmation

## More Information
