# 10. Buffer flush threading solution

Date: 2026-03-18
decision-makers: Ila Hadi-Assar
consulted: Kerstin Keller
informed: eCAL Team

## Status

Accepted

## Context and Problem Statement

The main thread gets occupied when flushing the buffer, so a seperate thread needs to handle the writing operations.


## Considered Options

* lock buffer when writing
    - ✅ memory effiecient
    - ❌ leads to delays because the main thread needs to wait for writing
* use double buffering to avoid blocking the main thread for file writing
    - ✅ allows concurrency
    - ❌ not effiecient
* use concurrent queue as buffer
    - ✅ effiecient handling of concurrent usage
    - ❌ external library

## Decision Outcome

Chosen option: "use double buffering to avoid blocking the main thread for file writing", because it can be implemented quickly and it can be done with feasible effort

### Consequences

* Good, because its implemented quickly
* Bad, because it ist the ideal solution

## More Information
