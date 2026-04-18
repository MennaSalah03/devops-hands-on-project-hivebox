[![Dynamic DevOps Roadmap](https://img.shields.io/badge/Dynamic_DevOps_Roadmap-559e11?style=for-the-badge&logo=Vercel&logoColor=white)](https://devopsroadmap.io/getting-started/)
[![Community](https://img.shields.io/badge/Join_Community-%23FF6719?style=for-the-badge&logo=substack&logoColor=white)](https://newsletter.devopsroadmap.io/subscribe)
[![Telegram Group](https://img.shields.io/badge/Telegram_Group-%232ca5e0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/DevOpsHive/985)
[![Fork on GitHub](https://img.shields.io/badge/Fork_On_GitHub-%2336465D?style=for-the-badge&logo=github&logoColor=white)](https://github.com/DevOpsHiveHQ/devops-hands-on-project-hivebox/fork)

# HiveBox - DevOps End-to-End Hands-On Project

<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox" style="display: block; padding: .5em 0; text-align: center;">
    <img alt="HiveBox - DevOps End-to-End Hands-On Project" border="0" width="90%" src="https://devopsroadmap.io/img/projects/hivebox-devops-end-to-end-project.png" />
  </a>
</p>

The project aims to cover the whole Software Development Life Cycle (SDLC). That means each phase will cover all aspects of DevOps, such as planning, coding, containers, testing, continuous integration, continuous delivery, infrastructure, etc.

---
## Current Progress
Phase | Progress 
--- | --- 
Phase 1 | Done
Phase 2 | Done
Phase 3 | In progress...
Phase 4 | Not Started
Phase 5 | Not Started
Phase 6 | Not Started
Phase 7 | Not Started


## Phases 1 and 2: Introduction and DevOps Core

For these phases, the project is just started. Phase 1 is the creation/forking of the repository and phase 2 is a small image creation for the app that at this stage only stores and prints the version of the app and also assigns it to the image tag.

The build is done by running the `build.sh` script in the repository's root directory, which:
1. runs the script responsible for getting the latest version
2. Building the app with the `Dockerfile` thereby generating the image with the current version.


## Phase 3

This Phase marks the beginning of using the Kanban Board to tackle the upcoming tasks. So far, their usage included adding the "backlog" tasks provided in the phase's instruction without much breaking tasks up just yet. This would need improvement in later phases.

This phase's highlight is the continuous integration with a tool like Github Actions (the one I will be using) or Jenkins. However, it also had another part, which is the app's API using a framework (Flask, Fastapi or Django). I have opted to choose fastapi because it seemed competent, but not too simple as I have heard when researching Flask.

It took about ~8 hours to reach the state of having the `/version` and the `/temperature` endpoints to be created successfully.

TBC...