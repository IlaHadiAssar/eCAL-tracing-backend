---
status: accepted
date: 03.03.2026
decision-makers: Ila Hadi-Assar
consulted: Kerstin Keller
informed: eCAL Team
---

# Use Python as programming language

## Context and Problem Statement
For the implementation of the tracing backend outside of eCAL there were no strict guidelines, which defined the programming language.


## Considered Options

* C++
    - :heavy_check_mark: most likely more efficient
    - :x: OpenTelemetry library not available as package
* Python
    - :heavy_check_mark: easy depency management
    - :heavy_check_mark: faster results
    - :x: likely less efficient

## Decision Outcome

Chosen option: "Python", because it's simpler and faster to implement

### Consequences

* Good, because it allows easy support of the OpenTelemetry library
* Bad, because there might be some performance drawbacks

## More Information
Performance drawbacks aren't a huge concern since the tracing backend doesn't interfere with eCAL's core communication.
