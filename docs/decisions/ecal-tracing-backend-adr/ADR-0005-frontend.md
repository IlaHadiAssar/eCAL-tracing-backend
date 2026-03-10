---
status: accepted
date: 03.03.2026
decision-makers: Ila Hadi-Assar
consulted: Kristof Hannemann
informed: eCAL Team
---

# Use Jaeger UI frontend

## Context and Problem Statement
Traces need to be visualized to be able to analyse them. There are several frontends available mostly used for distributed tracing in Microservice Architectures.

## Considered Options

* Grafana+Tempo
    - :heavy_check_mark: lots of analytic tools available
    - :heavy_check_mark: widely used
    - :x: complex setup
    - :x: distribution isn't straight forward
* Jaeger UI
    - :heavy_check_mark: very simple setup
    - :heavy_check_mark: easy distribution via docker-compose
    - :x: lacks tools for in depth analysis

## Decision Outcome

Chosen option: "Jaeger UI", because the setup is much simpler.

### Consequences

* Good, because anyone can setup a tracing frontend by simply running a docker-compose file
* Bad, because no in depth analysis possible in frontend

## More Information
A switch to Grafana+Tempo might happen in the future if more analytic tools are needed
