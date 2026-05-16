[![Dynamic DevOps Roadmap](https://img.shields.io/badge/Dynamic_DevOps_Roadmap-559e11?style=for-the-badge&logo=Vercel&logoColor=white)](https://devopsroadmap.io/getting-started/)
[![Community](https://img.shields.io/badge/Join_Community-%23FF6719?style=for-the-badge&logo=substack&logoColor=white)](https://newsletter.devopsroadmap.io/subscribe)
[![Telegram Group](https://img.shields.io/badge/Telegram_Group-%232ca5e0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/DevOpsHive/985)
[![Fork on GitHub](https://img.shields.io/badge/Fork_On_GitHub-%2336465D?style=for-the-badge&logo=github&logoColor=white)](https://github.com/DevOpsHiveHQ/devops-hands-on-project-hivebox/fork)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/MennaSalah03/devops-hands-on-project-hivebox/badge)](https://scorecard.dev/viewer/?uri=github.com/MennaSalah03/devops-hands-on-project-hivebox)

  
  
# HiveBox - DevOps End-to-End Hands-On Project

<p align="center">
<a href="https://devopsroadmap.io/projects/hivebox" style="display: block; padding: .5em 0; text-align: center;">
<img alt="HiveBox - DevOps End-to-End Hands-On Project" border="0" width="90%" src="https://devopsroadmap.io/img/projects/hivebox-devops-end-to-end-project.png" />
</a>
</p>


PS: stay tuned for my attempt at making an alternative logo for the project :D

This multi-phase project is mainly for learning purposes and aims to cover the whole Software Development Life Cycle (SDLC). That entails that the phases would cover all aspects of DevOps, such as planning, coding, containers, orchestration, various types of testing, continuous integration, continuous delivery, infrastructure, etc.

If you are attempting to do this project or a similar fashioned one, I have compiled most of the resources that helped me throughout my journey, you can find it in the `docs/RESOURCES.md` file or [here](https://github.com/MennaSalah03/devops-hands-on-project-hivebox/blob/main/docs/RESOURCES.md))

The final architecture of the project:

![hivebox](https://devopsroadmap.io/assets/images/hivebox-architecture-a7fe504c22027e87b6f7b188cd57d2d8.png)

---
## Current Progress

| Phase   | Progress   |
| ------- | ---------- |
| Phase 1 | ✅ Done     |
| Phase 2 | ✅ Done     |
| Phase 3 | ✅ Done     |
| Phase 4 | ⏳ WIP (25%)     |
| Phase 5 | ♾️ Pending |
| Phase 6 | ♾️ Pending |

current repository structure:

```
.
├── Dockerfile
├── README.md
├── build.sh
├── docs
│   └── RESOURCES.md
├── .github/workflows
|	├── hivebox-ci.yml
|	└── scorecard.yml
├── src
│   ├── main.py
│   ├── print_version.py
│   └── version.txt
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_app.py
│   └── test_version_printer.py	
├── k8s_manifests
|	├── kind.yaml
|	├── hivebox-confimap.yaml
|	├── hivebox-deployment.yaml
|	└── hivebox-service.yaml
├── pyproject.toml
└── uv.lock
```

Current Tech Stack:
- Backend: Python 3.12, FastAPI
- Package Manager: uv
- Testing: Pytest, MockMagic (unittest)
- CI/CD: GitHub Actions
- Observability: Prometheus (python's prometheus-client)
- Security: OpenSSF Scorecard, Hadolint
- Orchestration: Kubernetes (KIND, kubectl)
- Registry: Docker Hub

### How to Use the App
Pull the image from [DockerHub](https://hub.docker.com/repository/docker/menna011/hivebox/general) and run it

```
docker run --rm -d -p 8000:8000/tcp hivebox:latest
```
*Access the API at http://localhost:8000 or view the docs at http://localhost:8000/docs.*

For developer setup:
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
2. Sync environment: `uv sync`
3. Run Tests using pytest: `pytest tests/`
4. Install KIND
5. Local Build: bash build.sh (This script handles local image creation). Ensure it's executable before running. `chmod +x build.sh`

### App's API Endpoints:
All the current endpoints are `GET` requests that retreives data from the API.
- `/`: Welcome message `{"message": "Welcome to HiveBox"}`
- `/version`: Returns current SemVer `{"version": "1.2.0"}`
- `/temperature`: Returns global temperature sensors average `"{"average_temperature": 22.5}`
- `/metrics`: Returns metrics about the `/temperature` endpoint (Counter for reuests, Gauge of the current average temperature, and the interval for data to load).

## Phase 1 & Phase 2: Project Foundation

In phases 1 and 2, we start to to set up our working tree and experiment with project management tools and git best practices we will be using in the next phases.

### Phase Deliverables:
- Forking the original repository.
- Understanding how to operate a repo as if in a team setting and good practices like working on separate branches and using PRs to merge to main.
- Deciding on an Agile methodology (Kanban)
- Learning about scope creep and how to avoid it.
- Creating a basic `Dockerfile` for the project with some best practices applied (optimal base image, run with non-root user).
- Using `uv` for dependency management instead of `requirements.txt`.
- Learning and using Semantic Versioning for repository tags and docker images for ensuring absolute traceability between the code base and docker images.
## Personal Technical Growth
- Automating the app build with having a script to run instead of manual error-prone CLI commands.
- Understanding Semantic versioning and integrating it in the build process.

### Technical Challenges & Engineering Decisions
- Kanban: GitHub has a built-in Kanban board feature on GUI which is highly accessible to use especially for a solo-developed project and it hasn't been complicated so far. It was also the roadmap's recommended methodology for the project.
## Phase 3: Start - Laying the Base
start date: 28/2/2026.<br>
finish date: 19/4/2026.<br>
time taken: 30+ hrs.

### Phase Deliverables:
- Creation of the app's API (I used [FastAPI](https://fastapi.tiangolo.com/)) with 2 endpoints required.
	- `/version` to display the supposed current app's version.
	- `/temperature` to display the average temperature of **all** sensor-boxes across the globe from the [OpensenseAPI](https://docs.opensensemap.org/#api-_).
	- The root endpoint have been added with a welcome message to not cause unnecessary error if accessed.
- Unit testing the code using `pytest`.
* Applying more of Docker's Best practices. 
	* Use Dockerfile linter (`hadolint`).
	* using `HEALTHCHECK`.
	* Use `ENTRYPOINT` with `CMD`.
	* Avoid any unnecessary files (using `.dockerignore`)

* Creating a continuous integration pipeline (I chose GitHub Actions for implementation) to include
	* Linting the python code (Pylint) and Dockerfile (Hadolint).
	* Building the app's image with Docker
	* Unit testing the app.
	* Setting up an OSSF scoreboard.


### Personal Technical Growth
- Exploration of APIs using the `OpensenseAPI` and it's docs.
- Learning FastAPI to create `/temperature` and `/version` endpoints and more about APIs in general.
- Doing unit tests with  `pytest` and `unittest`'s `MockMagic` (helped with creating mock data for testing endpoints).
- Getting better at using git above the level of just basic commits and pushes.
	- Using the `--amend` flag for editing my commits and messages freely
	- Understanding and using tags efficiently in SemVer.
	- Successfully creating my first PR and merge to main.
- Using GitHub Actions for the first time in an automated pipeline of a real project.
- Creating and using repository-wide secrets for docker hub credentials.
- Got a better grasp on management of tasks and issues using the Kanban board.

### Technical Challenges & Engineering Decisions
- GitHub Actions: Simpler to use, especially for doing pipelines for the first time, already built in GitHub for immediate use, and uses `yaml` files for configuration.
- FastAPI: Modern, Async, type hinting and it also has a moderate learning curve between Flask and Django. 
- Pytest: code efficiency as  it has fixtures which helps reducing the repetition in the code, easy to write and understand and integrates seamlessly with modern automation tools

### What I'd change for next phases
Practices and habits:
- Using the Kanban board more frequently and efficiently even for small issues.
- Doing Pull requests semi-daily.
- Documenting daily achievements and fails (keeping a dev diary).
- Dedicating more time for theory and focused research.
- Having more strict time deadlines for features.
Technical additions:
- Adding image promotion (to latest) conditions.
- Fixing vulnerabilities suggested by OSSF scoreboard (score is 3.6/10) and giving higher priority to learning and applying security practices.
- Learning to link fixed issues to commits.
---

## Phase 4: Expand - Constructing a Shell
Start date: 2/5/2026 <br>
Finish date: Still in progress<br>
Time taken: 4+ hrs.<br>

### Phase Deliverables

- Ensuring the senseboxes configurable by env vars.
- Creating a `/metrics` endpoint that contain metrics for the app's endpoints
- Editing the `/temperature` endpoint to include a status field indicating the average temperature range.
  - Less than 10: Too Cold
  - Between 11-36: Good
  - More than 37: Too Hot
- Create a KIND configuration to run with Ingress-Nginx.
- Create Kubernetes core manifests to deploy the application.
- Create and run integration tests for the app.
- Run SonarQube for code quality, security, and static analysis.
- Run Terrascan for Kubernetes manifest misconfigurations and vulnerabilities.
- Apply Best Practices for CI.
- Create a GitHub Actions workflow for CD with a step to release by pushing a versioned Docker image to a container registry.

### Personal Technical Growth



### Technical Challenges & Engineering Decisions

---
*This Project is Part of my YearOfDevOps journey which I post regularly about on [Twitter/X](https://x.com/Menna_Salah03)*
