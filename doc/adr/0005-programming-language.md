# 5. Programming language

Date: 2026-03-18
decision-makers: Ila Hadi-Assar
consulted: Kerstin Keller
informed: eCAL Team

## Status

Accepted

## Context and Problem Statement
For the implementation of the tracing backend outside of eCAL there were no strict guidelines, which defined the programming language.


## Considered Options

* C++
    - ✅ most likely more efficient
    - ❌ OpenTelemetry library not available as package
* Python
    - ✅ easy depency management
    - ✅ faster results
    - ❌ likely less efficient

## Decision Outcome

Chosen option: "Python", because it's simpler and faster to implement

### Consequences

* Good, because it allows easy support of the OpenTelemetry library
* Bad, because there might be some performance drawbacks

## More Information
Performance drawbacks aren't a huge concern since the tracing backend doesn't interfere with eCAL's core communication.
