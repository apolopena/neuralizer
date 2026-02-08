# TASKS.md — Running Ledger

> **Task Codes:** BOOTSTRAP-X for pre-plan foundation | POST-IMPL-X for substantial implementations | MAINT-X for maintenance (fixes, tweaks, refactoring)
>
> **Ordering:** Newest entries at top.

---

## In Progress
<!-- IN_PROGRESS_START -->
- *(empty)*
<!-- IN_PROGRESS_END -->

## Done
<!-- DONE_START -->
- [x] PI-3: Scrubbing Pipeline with MCP Tools & Error Handling (2026-02-07)
  - MCP server with scrub_prompt/scrub_log_as_prompt/scrub_log_as_file tools via stdio transport
  - Tokenizer with span-based replacement (longest match wins for overlaps)
  - PathSandbox utility for path traversal prevention
  - MCP client with async subprocess communication, auto-restart, 30s timeout
  - File upload interception route with MIME validation, detection, scrubbing flow
  - Chat completions route with detection→scrubbing→publish orchestration
  - Neuralizer detect() method with item_types inference, fail-closed error handling
  - Debug trace system (middleware + WebSocket) gated by DEV_MODE
  - Comprehensive unit tests (tokenizer, patterns, scrubber, path sandbox, MCP client)
  - Integration tests for Open WebUI schema compatibility
- [x] PI-2: Header, Scrubbing Mode Toggle & Interception Control (2026-02-06)
  - AppHeader with branded logo, stateful scrubbing pill toggle (confirmation UX), settings gear
  - GSAP-powered mode switching: animated panel resize 50/50 ↔ 0/100
  - SettingsDrawer sliding panel with backdrop, escape-key, placeholder scrubbing settings
  - CSS design tokens (:root custom properties), prefers-reduced-motion support, useGsap composable
  - Backend scrubbing mode toggle: GET/POST /v1/mode, LLM proxy passthrough in free chat mode
  - Frontend syncs mode state with backend on mount and toggle
- [x] MAINT-1: PRP Templates + AI Provenance Workflow (2026-02-06)
  - PRP planning templates (proposal_standalone, prp_standalone, prp_bulk)
  - AI provenance workflow via gh-dispatch-ai.yml with LearnStream Claude AI GitHub App
- [x] PI-1: Multi-Environment Deployment Configuration (2026-02-06)
  - COMPOSE_FILE-driven GPU overrides (CUDA/Vulkan/CPU), HTTP-by-default with HTTPS opt-in
  - Parameterized Caddy ports (HTTP_PORT, OPENWEBUI_PORT), switchable Caddyfile mount
  - Dynamic iframe URL via window.location + Vite env, bootstrap-iframe.sh for server deployments
  - Simplified stack.sh using --project-directory, removed --dev flag
  - Rewrote .env.sample with comprehensive documentation
- [x] BOOTSTRAP-5: Agent Framework + Neuralizer Detection (2026-02-04)
  - Agent framework ported from catalytic-customer: BaseAgent ABC, BaseClient ABC, AgentActivityMonitor, AgentEvent model
  - Neuralizer agent classifies prompts for PII, credentials, log files, code secrets, infrastructure via local LLM
  - LlamaCppClient with configurable `LLM_TIMEOUT` env var, MockThinkingClient for testing JSON parse errors
  - Detection system prompt with few-shot examples, false-positive tuning for container/CLI output
  - Prompt builders in `services/prompts/neuralizer.py` (detect prompt, panel response, status response)
  - Human-readable error reporting: timeout, connection, JSON parse errors with actionable guidance
  - Test endpoint `/v1/test/think-error` for deterministic error scenario testing
  - Env vars: `LLM_MODEL` (switchable thinking/instruct), `LLM_TIMEOUT`, both models in `.env.example`
- [x] BOOTSTRAP-4: Open WebUI + Prompt Interception Proxy (2026-02-04)
  - Open WebUI service with telemetry disabled, Caddy dedicated port (8082) for iframe embedding
  - Prompt proxy (`/v1/chat/completions`) intercepts prompts, publishes to Redis, blocks LLM forwarding
  - WebSocket `/ws/prompts` streams intercepted prompts to frontend via Redis pub/sub
  - Split-pane Vue layout: SanitizedPanel (left, real-time prompts) + ChatPanel (right, Open WebUI iframe)
- [x] BOOTSTRAP-3: LLM Inference Service (2026-02-04)
  - llama.cpp server-cuda container serving Qwen3-4B GGUF with GPU offload, configurable context window
  - Env vars `LLM_IMAGE` and `LLM_CONTEXT_SIZE` for GPU backend and context size switching
  - Health endpoint reports Redis + LLM dependency status (`ok`/`degraded`/`unavailable`)
  - Consistent `neuralizer-` container naming, curl in backend image, `scripts/llm/smoke-test.sh` with spinner
- [x] BOOTSTRAP-2: Stack Scaffolding (2026-02-04)
  - Docker Compose with Caddy, FastAPI backend, Vue 3 frontend, Redis (7-alpine, AOF, healthcheck)
  - Backend: uvicorn + wsproto WebSocket, Redis lifespan, health endpoint; Frontend: Vue 3 + Tailwind 4 + Vite 7
  - `scripts/stack.sh` (up/down/restart/rebuild/logs/status, --dev flag), Caddyfile reverse proxy
  - `docs/setup.md` with draft steps, `stack/models/` gitignored for Qwen3-4B GGUF
- [x] BOOTSTRAP-1: Project Scaffolding & Tooling (2026-02-03)
  - `.ai/` planning system (PLANNING/TASKS templates, PRD/PRP structure), `.claude/` agent orchestration
  - `scripts/git-ai.sh` SSH wrapper with AI attribution, `.claude/settings.json` permissions
  - Slash commands: generate-prp, execute-prp, generate-context, generate-arch, prime-full/quick
  - README with logo, CHANGELOG, CLAUDE.md with multi-agent workflow instructions
<!-- DONE_END -->

## Abandoned
