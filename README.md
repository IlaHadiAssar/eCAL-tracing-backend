# eCAL-tracing-backend

OpenTelemetry tracing backend for eCAL publisher/subscriber spans. Reads span data from JSON files and exports traces to Jaeger with proper context propagation (publish → receive → callback).

## Install

For a normal local install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

For development:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

If you prefer installing the CLI into an isolated user environment, `pipx` also works:

```bash
pipx install .
```

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
pip install -e .[dev]
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

You can also run the installed package as a module:

```bash
source .venv/bin/activate
python -m ecal_tracing_backend
```

Traces will be exported to Jaeger via OTLP HTTP on port 4318.

## Build and Release

GitHub Actions builds a source distribution and wheel on every push and pull request.

To cut a release, create and push a version tag that starts with `v`, for example:

```bash
git tag v0.1.0
git push origin v0.1.0
```

That tag triggers the release job, which attaches the built `dist/*` artifacts to a GitHub release with generated notes.

If you only want to verify packaging, you can run the same command locally:

```bash
python -m build
```
