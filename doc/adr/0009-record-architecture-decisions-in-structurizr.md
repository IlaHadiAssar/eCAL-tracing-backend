# 9. Record architecture decisions in structurizr

Date: 2026-03-18
decision-makers: Ila Hadi-Assar
consulted: Kristof Hannemann
informed: eCAL Team

## Status

Supercedes [1. Record architecture decisions](0001-record-architecture-decisions.md)

Accepted

## Context and Problem Statement

Architecture decisions aren't documented yet.


## Considered Options

* Confluence Page
    - ✅ most flexible
    - ❌ not a dedicated solution for software architecture
    - ❌ often overlooked
* MADR
    - ✅ quick and simple format
    - ✅ close to code so it wont be overlooked as much
    - ❌ doesnt include other architecture artifects
* Structurizr
    - ✅ dedicated solution for all architecture needs
    - ✅ GUI makes things more visible
    - ✅ ADRs stay close to code
    - ✅/❌ adr-tools is now required to create adrs
    - ❌ more complicated usage


## Decision Outcome

Chosen option: "Structurizr", because it offers more a structurized approach for Software Architecture.
Including a GUI for ADRs as well as Software Diagrams.

### Consequences

* Good, because it adds documentation
* Neutral, the use of adr-tools for creating adrs is now pretty much necessary
* Bad, because it takes time

## More Information
