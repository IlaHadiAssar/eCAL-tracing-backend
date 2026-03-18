# 4. Data buffering solution

Date: 2026-03-17
decision-makers: Ila Hadi-Assar
consulted: Kerstin Keller
informed:

## Status

Accepted

## Context and Problem Statement
eCAL potentially produces thousands of traces every minute. Constantly sending these traces or writing them to a file will produce too much overhead, so traces need to be buffered and processed in batches.


## Considered Options

* buffering each type of span in its own buffer
    - ✅ best memory efficiency
    - ❌ most boilerplate code
* buffering all types of spans in a variant vector
    - ✅ most flexible solution
    - ❌ adds most overhead both in memory and computation
* buffering a single unified spantype
    - ✅ fastest computation
    - ✅ minimal loss in memory efficiency
    - ❌ unused fields in unfied datatype
    - ❌ high maintenance


## Decision Outcome

Chosen option: "buffering a single shared datatype in one vector", because the memory overhead of a shared datatype is minimal, since the spans only have 1 distinctive attribute.

### Consequences

* Good, because simple implementation and simple mapping in backend
* Bad, because buffer flushing is less flexible with no distinction between publisher and subscriber spans

## More Information
The decisions are based on theory. Benchmarks would give more accurate results, as too which method is most efficient.
