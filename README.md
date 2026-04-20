# eCAL-tracing-backend

OpenTelemetry tracing backend for eCAL publisher/subscriber spans. Reads span data from JSON files and exports traces to Jaeger with proper context propagation (publish → receive → callback).

## Setup (Ubuntu)

### Prerequisites

```bash
sudo apt update
sudo apt install python3 python3-venv docker.io docker-compose
```

### Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Start Jaeger

```bash
sudo docker-compose up -d
```

Jaeger UI will be available at http://localhost:16686.

### Run

Place your eCAL span JSON files in `data/` (`ecal_publisher_spans.json` and `ecal_subscriber_spans.json`), then:

```bash
source .venv/bin/activate
python3 src/main.py
```

Traces will be exported to Jaeger via OTLP HTTP on port 4318.
