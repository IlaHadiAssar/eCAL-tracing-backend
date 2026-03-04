---
status: accepted
date: 03.03.2026
decision-makers: Ila Hadi-Assar
consulted: Kerstin Keller, Kristof Hannemann
informed: eCAL Team
---

# Implement a tracing backend outside of eCAL's core

## Context and Problem Statement
Creating high amounts of Traces and uploading them to a frontend requires a lot of computation and adds external dependencies if you want Compliance with OpenTelemetry which is widely supported for tracing frontends

## Considered Options

* Implement custom solution inside eCAL with full tracing support
* Export minimal traces and handle logic on a tracing backend


## Decision Outcome

Chosen option: "Export minimal traces and handle logic on a tracing backend"
### Consequences

* Good, because overhead in eCAL is kept to a minimum
* Bad, because another repository has to be maintained

### Confirmation



## Pros and Cons of the Options

### Export minimal traces and handle logic on a tracing backend

* Good, because all dependencies are "outsourced" from eCAL core project
* Good, because overhead is minimized
* Bad, because another repository has to be maintained
## More Information
