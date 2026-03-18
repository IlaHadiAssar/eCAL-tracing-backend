# 6. Frontend

Date: 2026-03-18

## Status

Accepted

## Context and Problem Statement
Traces need to be visualized to be able to analyse them. There are several frontends available mostly used for distributed tracing in Microservice Architectures.

## Considered Options

* Grafana+Tempo
    - :heavy_check_mark: lots of analytic tools available
    - :heavy_check_mark: widely used
    - ❌ complex setup
    - ❌ distribution isn't straight forward
* Jaeger UI
    - :heavy_check_mark: very simple setup
    - :heavy_check_mark: easy distribution via docker-compose
    - ❌ lacks tools for in depth analysis

## Decision Outcome

Chosen option: "Jaeger UI", because the setup is much simpler.

### Consequences

* Good, because anyone can setup a tracing frontend by simply running a docker-compose file
* Bad, because no in depth analysis possible in frontend

## More Information
A switch to Grafana+Tempo might happen in the future if more analytic tools are needed
