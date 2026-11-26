[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/MennaSalah03/devops-hands-on-project-hivebox/badge)](https://scorecard.dev/viewer/?uri=github.com/MennaSalah03/devops-hands-on-project-hivebox)
![CI](https://github.com/MennaSalah03/devops-hands-on-project-hivebox/actions/workflows/hivebox-ci.yml/badge.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)

# HiveBox - DevOps End-to-End Hands-On Project

<p align="center">
<a href="https://devopsroadmap.io/projects/hivebox" style="display: block; padding: .5em 0; text-align: center;">
<img alt="HiveBox - DevOps End-to-End Hands-On Project" border="0" width="90%" src="https://devopsroadmap.io/img/projects/hivebox-devops-end-to-end-project.png" />
</a>
</p>

HiveBox is a containerized environmental telemetry service that ingests real-time global temperature data from the [openSenseMap API](https://github.com/sensebox/openSenseMap-API/tree/master), caches it in Valkey for low-latency reads, and archives historical snapshots to MinIO.

The Goal: Rather than stopping at a working API, HiveBox is engineered to solve the operational problems of running a backend service in production—decoupling client requests from slow upstream APIs, validating data freshness via Kubernetes readiness probes (/readyz), exposing Prometheus metrics, and automating the path from commit to cluster through security-scanned CI/CD pipelines.

If you are attempting to do this project or a similar one, I have compiled most of the resources that helped me throughout my journey, you can find it in the `docs/RESOURCES.md` file or [here](https://github.com/MennaSalah03/devops-hands-on-project-hivebox/blob/main/docs/RESOURCES.md))

The final architecture of the project:

![hivebox](https://devopsroadmap.io/assets/images/hivebox-architecture-a7fe504c22027e87b6f7b188cd57d2d8.png)

---

## Repository structure:

```
.
├── build.sh
├── docker-compose.yaml
├── Dockerfile
├── docs
│   ├── DEVLOG.md
│   └── RESOURCES.md
├── k8s_manifests
│   ├── hivebox-confimap.yaml
│   ├── hivebox-deployment.yaml
│   ├── hivebox-ingress.yaml
│   ├── hivebox-service.yaml
│   └── kind.yaml
├── main.py
├── pyproject.toml
├── README.md
├── src
│   ├── config.py
│   ├── main.py
│   ├── metrics.py
│   ├── print_version.py
│   ├── services.py
│   ├── temperature.py
│   └── version.txt
├── tests
│   ├── conftest.py
│   ├── __init__.py
│   ├── test_integration_app.py
│   ├── test_unit_app.py
│   └── test_version_printer.py
└── uv.lock
```

Current Tech Stack:
- Backend: Python 3.12, FastAPI
- Package Manager: uv
- Testing: Pytest, unittest
- Cache: Valkey
- Storage: MinIO
- CI/CD: GitHub Actions
- Observability: Prometheus
- Security: OpenSSF Scorecard
- Lining: Ruff, Hadolint
- Orchestration: Kubernetes
- Registry: github container registry (ghcr.io)

### How to Use the App
For developer local setup:
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
2. Sync environment: `uv sync`
3. Run Tests using pytest: `pytest tests/`
4. Install KIND
5. Local Build: bash build.sh (This script handles local image creation). Ensure it's executable before running. `chmod +x build.sh`

### App's API Endpoints:
`GET` endpoints:
- `/`: Discplays Welcome message `{"message": "Welcome to HiveBox"}`
- `/version`: Returns current SemVer `{"version": "1.2.0"}`
- `/temperature`: Returns global temperature sensors average `"{"average_temperature": 22.5}`
- `/metrics`: Returns metrics about the `/temperature` endpoint (Counter for reuests, Gauge of the current average temperature, and the interval for data to load).
- `/readyz`:
`POST` endpoints
- `/cache`
- `/store`


### CI/CD
```
push changes to main
├── CI runs lint ✅
├── CI runs tests (unit and integration tests) ✅
├── CI builds hivebox:SHA ✅
├── CI pushes :ci-candidate to GHCR ✅
├── CI uploads version artifact ✅
└── Terrascan, OSSF scoreboard, SAST jobs run and upload sarif files to GitHub ✅
      ↓
CD triggered
├── pulls :ci-candidate
├── Create KIND cluster and spin up the pod(s).
├── Verify rollout
└── pushes final tags ✅
```
