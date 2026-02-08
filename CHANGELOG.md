# Changelog

All notable changes to this project will be documented in this file.

## [v0.1.0](https://github.com/apolopena/neuralizer/releases/tag/v0.1.0)

### [PR #11](https://github.com/apolopena/neuralizer/pull/11) - PI-3: MCP Scrubbing Pipeline & Debug Tracing

**Branch:** PI-3_scrubbing-pipeline → main

**Status:** ✅ Merged

#### PI-3: MCP Scrubbing Pipeline & Debug Tracing

- [[651f8d9](https://github.com/apolopena/neuralizer/commit/651f8d9)] **DOCS:** *reference*
  - Add Anthropic model names reference in `.ai/docs/anthropic/model-names.md`

- [[f7ae0bb](https://github.com/apolopena/neuralizer/commit/f7ae0bb)] **FEAT:** *scrubbing-pipeline*
  - MCP scrubbing server via FastMCP subprocess with JSON-RPC protocol
  - Span-based tokenizer for PII replacement (prevents over-scrubbing)
  - Log patterns: IP, private IP, internal URL, timestamp, endpoint, user, terminal_user
  - Standard patterns: email, phone, name, API key, secret, bearer token, path, resource ID
  - Terminal user pattern for `whoami`, `id`, `logname` command output
  - File upload endpoint with sandbox path validation
  - Debug trace middleware with WebSocket streaming (`/ws/debug`)
  - `DebugPanel.vue` draggable debug trace viewer (dev mode only)
  - Processing indicator in left panel before detection runs
  - Fail-closed behavior on detection errors
  - Config API for frontend feature flags (`/api/config`)
  - Auto-scrolling `SanitizedPanel.vue` with shield emoji status
  - Unit tests for tokenizer, scrubber, patterns, MCP client, path sandbox

---

**System Status:** ✅ MCP scrubbing pipeline with comprehensive PII detection operational
**PI-3 Focus:** ✅ FastMCP subprocess server | ✅ Span-based tokenizer | ✅ Log and standard patterns | ✅ File upload with sandbox validation | ✅ Debug trace WebSocket streaming
**Maintenance:** ✅ Config API for feature flags | ✅ Fail-closed error handling | ✅ MCP subprocess auto-restart

---

## [v0.0.4](https://github.com/apolopena/neuralizer/releases/tag/v0.0.4)

### [PR #6](https://github.com/apolopena/neuralizer/pull/6) - PI-2: Header, Scrubbing Mode Toggle & Interception Control

**Branch:** ap-dev-working3 → main

**Status:** ✅ Merged

#### PI-2: Header, Scrubbing Mode Toggle & Interception Control

- [[d42c0be](https://github.com/apolopena/neuralizer/commit/d42c0be)] **FEAT:** *frontend*
  - Add scrubbing mode toggle with backend proxy integration via GET/POST `/v1/mode` and LLM passthrough in free chat mode

- [[169c6b7](https://github.com/apolopena/neuralizer/commit/169c6b7)] **FEAT:** *infrastructure*
  - Add `recreate` command to `stack.sh` for full service recreation with compose files and environment handling

- [[66140ad](https://github.com/apolopena/neuralizer/commit/66140ad)] **DOCS:** *config*
  - Update WebSocket reference in `CLAUDE.md` from `/ws/` to `/ws/prompts` for real-time prompt streaming

- [[17fe1af](https://github.com/apolopena/neuralizer/commit/17fe1af)] **FIX:** *config*
  - Fix ruff command in `CLAUDE.md` to use `uv tool run` for proper environment isolation

- [[6203bdf](https://github.com/apolopena/neuralizer/commit/6203bdf)] **FEAT:** *frontend*
  - Add `AppHeader` with branded logo, stateful scrubbing pill toggle with confirmation UX, settings gear icon, GSAP-powered animated panel resize (50/50 to 0/100), `SettingsDrawer` sliding panel with backdrop and escape-key support, CSS design tokens via `:root` custom properties, prefers-reduced-motion support, and `useGsap` composable; add SVG prohibition overlay on logo during scrubbing disabled with GSAP stroke draw animation

- [[fe6d554](https://github.com/apolopena/neuralizer/commit/fe6d554)] **CHORE:** *config*
  - Add deferred directory to `.gitignore`

- [[b315b3d](https://github.com/apolopena/neuralizer/commit/b315b3d)] **DOCS:** *config*
  - Add `uv` and `.venv` directive to `CLAUDE.md` for Python environment management

- [[fe169b7](https://github.com/apolopena/neuralizer/commit/fe169b7)] **DOCS:** *config*
  - Add UX designer role prompt to `.claude/` directory

---

**System Status:** ✅ Header UI with scrubbing mode toggle operational
**PI-2 Focus:** ✅ AppHeader with logo and mode toggle | ✅ GSAP panel animations | ✅ Backend scrubbing mode control | ✅ Frontend/backend sync | ✅ SVG prohibition overlay with animation
**Maintenance:** ✅ stack.sh rebuild/recreate commands | ✅ CLAUDE.md updated with uv directives and WebSocket reference

---

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
