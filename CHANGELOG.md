# Changelog

All notable changes to this project will be documented in this file.

## [v0.0.3](https://github.com/apolopena/neuralizer/releases/tag/v0.0.3)

### [PR #5](https://github.com/apolopena/neuralizer/pull/5) - PI-1: Multi-Environment Deployment Configuration

**Branch:** ap-dev-working → main

**Status:** ✅ Merged

#### MAINT-1: PRP Templates + AI Provenance Workflow

- [[0b7a9fd](https://github.com/apolopena/neuralizer/commit/0b7a9fd)] **CHORE:** *planning*
  - Add PRP planning templates in `.ai/planning/prp/templates/` with proposal_standalone, prp_standalone, and prp_bulk for project planning

- [[86b043b](https://github.com/apolopena/neuralizer/commit/86b043b)] **CHORE:** *ci*
  - Add AI provenance workflow in `.github/workflows/gh-dispatch-ai.yml` with common scripts and sanity checks

#### PI-1: Multi-Environment Deployment Configuration

- [[1bb18c4](https://github.com/apolopena/neuralizer/commit/1bb18c4)] **FEAT:** *infrastructure*
  - Add multi-environment deployment config with COMPOSE_FILE-driven GPU overrides (CUDA, Vulkan, CPU), HTTP by default with HTTPS opt-in via `docker-compose.https.yml` and `Caddyfile.https`, parameterized Caddy ports, dynamic iframe URL via window.location, `bootstrap-iframe.sh` for server deployments, and comprehensive `.env.sample` documentation

---

**System Status:** ✅ Deployable on any machine — NVIDIA, AMD, Intel, or CPU-only
**PI-1 Focus:** ✅ COMPOSE_FILE-driven GPU overrides | ✅ HTTP default, HTTPS opt-in | ✅ Parameterized ports | ✅ Dynamic iframe URL | ✅ Simplified stack.sh
**MAINT-1 Focus:** ✅ PRP planning templates | ✅ AI provenance workflow via LearnStream Claude AI

---

## [v0.0.2](https://github.com/apolopena/neuralizer/releases/tag/v0.0.2)

### [PR #3](https://github.com/apolopena/neuralizer/pull/3) - Bootstrap WebUI and Agent Framework

**Branch:** dev-working → main

**Status:** ✅ Merged

#### BOOTSTRAP-4: Open WebUI + Prompt Interception Proxy

- [[ca20627](https://github.com/apolopena/neuralizer/commit/ca20627)] **FEAT:** *infrastructure*
  - Add Open WebUI service with telemetry disabled, Caddy dedicated port (8082) for iframe embedding, prompt proxy (/v1/chat/completions) that intercepts prompts and publishes to Redis, and WebSocket /ws/prompts for streaming intercepted prompts to frontend via Redis pub/sub

- [[71ffd7a](https://github.com/apolopena/neuralizer/commit/71ffd7a)] **FEAT:** *infrastructure*
  - Add stack scaffolding with `docker-compose.yml`, `docker-compose.dev.yml`, `Dockerfile` for backend, and `Caddyfile` configuration for multi-service orchestration

#### BOOTSTRAP-5: Agent Framework + Neuralizer Detection

- [[809cca9](https://github.com/apolopena/neuralizer/commit/809cca9)] **FEAT:** *agent-framework*
  - Add agent framework ported from catalytic-customer with `BaseAgent` ABC, `BaseClient` ABC, `AgentActivityMonitor`, `AgentEvent` model, and Neuralizer agent for PII/credentials/log/code/infrastructure detection via local LLM

- [[ecd05c8](https://github.com/apolopena/neuralizer/commit/ecd05c8)] **FEAT:** *inference*
  - Add LLM inference service with health checks, `LlamaCppClient` with configurable `LLM_TIMEOUT` env var, `MockThinkingClient` for testing JSON parse errors, detection system prompt with few-shot examples, and human-readable error reporting

- [[35f1801](https://github.com/apolopena/neuralizer/commit/35f1801)] **CHORE:** *testing*
  - Add LLM smoke test script with spinner for local testing of inference endpoints

---

**System Status:** ✅ Full prompt interception and detection pipeline operational
**BOOTSTRAP-4 Focus:** ✅ Open WebUI iframe embedding | ✅ Prompt interception proxy | ✅ WebSocket streaming via Redis pub/sub | ✅ Split-pane Vue layout
**BOOTSTRAP-5 Focus:** ✅ Agent framework (BaseAgent, BaseClient, AgentActivityMonitor) | ✅ Neuralizer PII/secrets detection via local LLM | ✅ LlamaCppClient with configurable timeout

---

## [v0.0.1](https://github.com/apolopena/neuralizer/releases/tag/v0.0.1)

### [PR #1](https://github.com/apolopena/neuralizer/pull/1) - Add project scaffolding and tooling

**Branch:** initial-setup → main

**Status:** ✅ Merged

#### BOOTSTRAP-1: Project Scaffolding & Tooling

- [[167b1e2](https://github.com/apolopena/neuralizer/commit/167b1e2)] **CHORE:** *setup*
  - Add project scaffolding and tooling with `.ai/` directory structure, `.claude/` commands and agents, `CLAUDE.md` instructions, scripts, and planning templates

- [[fa67cae](https://github.com/apolopena/neuralizer/commit/fa67cae)] **CHORE:** *config*
  - Add `.claude/settings.json` with permissions config, `.gitignore` for Python/Vue/Node/Docker/WSL, and supporting project configuration

### [PR #2](https://github.com/apolopena/neuralizer/pull/2) - Add README with logo and project intro

**Branch:** initial-setup → main

**Status:** ✅ Merged

#### BOOTSTRAP-2: README & Documentation

- [[1085aa1](https://github.com/apolopena/neuralizer/commit/1085aa1)] **DOCS:** *readme*
  - Add `README.md` with logo and project intro

---

**System Status:** ✅ Project scaffolding and tooling complete
**BOOTSTRAP-1 Focus:** ✅ .ai/ planning system | ✅ .claude/ agent orchestration | ✅ git-ai.sh SSH wrapper | ✅ Slash commands
**BOOTSTRAP-2 Focus:** ✅ README with logo and project intro | ✅ Docker Compose stack (Caddy, FastAPI, Vue 3, Redis, llama.cpp) | ✅ Health monitoring

---
