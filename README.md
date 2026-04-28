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

If you want to force a specific input directory, pass `--data-dir`:

```bash
source .venv/bin/activate
ecal-tracing --data-dir path/to/your/dir
```

If `--data-dir` is omitted, the backend resolves the input directory with the same priority as eCAL tracing output paths:

1. `ECAL_TRACE_DIR`
2. `ECAL_DATA/traces`
3. `~/.ecal`, which corresponds to the path where `ecal.yaml` is loaded, preferring `~/.ecal/traces` when present

If none of these are available, the backend exits with an error and asks for one of them to be configured.

Then run:

```bash
source .venv/bin/activate
ecal-tracing
```

Traces will be exported to Jaeger via OTLP HTTP on port 4318.
