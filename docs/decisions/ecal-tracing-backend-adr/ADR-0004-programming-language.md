---
status:
date:
decision-makers:
consulted:
informed:
---

# Use Python as programming language

## Context and Problem Statement
For the implementatio of the tracing backend outside of eCAL there were no strict guidelines, which defined the programming language.


## Considered Options

* C++
* Python

## Decision Outcome

Chosen option: "Python", because it's simpler and faster to implement

### Consequences

* Good, because it allows easy support of the OpenTelemetry library
* Bad, because there might be some performance drawbacks

### Confirmation



## Pros and Cons of the Options

### Python

* Good, because OpenTelemetry can be used easily
* Bad, because of potential performance drawbacks

## More Information
Performance drawbacks aren't a huge concern since the tracing backend doesn't interfere with eCAL's core communication.
