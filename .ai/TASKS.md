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
