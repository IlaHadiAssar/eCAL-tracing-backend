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
sudo docker-compose up -d jaeger
```

Jaeger UI will be available at http://localhost:16686.

### Run

Place your eCAL tracing JSONL files in `~/.ecal/traces`, then:

```bash
source .venv/bin/activate
ecal-tracing
```

To read from a different directory, pass `--data-dir`:

```bash
ecal-tracing --data-dir path/to/your/dir
```

Traces will be exported to Jaeger via OTLP HTTP on port 4318.
