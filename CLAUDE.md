# Claude Code Multi Agent Observability

## Instructions
> Follow these instructions as you work through the project.

### Code Exploration
Skip qa/, .ai/scratch/, tests/ when exploring implementation

### REMEMBER: Use source_app + session_id to uniquely identify an agent.
Every hook event will include a source_app and session_id. Use these to uniquely identify an agent.
For display purposes, we want to show the agent ID as "source_app:session_id" with session_id truncated to the first 8 characters.

### Commit Messages
<60 chars, brief, imperative mood

### CRITICAL: SSH Git Commands
ALWAYS use `./scripts/git-ai.sh` for git commands requiring SSH (commit, push, pull, fetch, clone, remote, ls-remote, submodule). Prevents SSH askpass errors via keychain + adds AI attribution.

### GitHub Operations
CRITICAL: Mark agent (subagent_type=mark) is responsible for ALL GitHub write operations (PRs, issues, comments, releases).
Mark gathers context and dispatches .github/workflows/gh-dispatch-ai.yml with proper provenance.

### Planning System
When using `/generate-prp` or `/execute-prp`, read `.ai/AGENTS.md` for complete planning workflow directives.

### Real-Time Updates
Two WebSocket composables exist for different purposes:
- `useAdminWebSocket.js` - Admin dashboard updates (user events, session changes)
- `useAgentWebSocket.js` - Agent activity streaming (inference events, errors)

Use the appropriate composable for your feature. Don't create new WebSocket connections unless adding a genuinely new real-time data source.

### AskUserQuestion Tool
Never use this tool. Ask questions directly in response text - the tool's UI prevents freeform answers and doesn't show all questions at once.

### Backend Testing & Linting
See `docs/unit-tests.md` for complete setup. Quick reference:
```bash
cd backend/tests && uv pip install -r requirements.txt  # Install/update deps
cd backend && uv run ruff check . && uv run ruff format .  # Lint
./scripts/run-tests.sh -m  # Run main backend tests
```

### CRITICAL: Docker Container Actions for Manual Testing
**When telling user to test changes, use the CORRECT Docker command:**
- **.env changed**: `docker compose up -d --force-recreate <service>` (restart does NOT reload .env!)
- **Python code changed**: `docker compose restart <service>`
- **requirements.txt changed**: `docker compose up -d --build <service>`
- **Dockerfile changed**: `docker compose up -d --build <service>`

Verify env vars loaded: `docker compose exec backend printenv VAR_NAME`
See `docs/backend/manual-testing.md` for full reference.

### RAG Service (rag-service/) Code Changes
`rag-service/backend/` is volume-mounted into the container. Code changes don't require rebuild - just restart:
`cd rag-service && docker compose -f docker-compose.yml -f docker-compose.dev.yml restart rag-service`
Only rebuild when `rag-service/backend/requirements.txt` or `rag-service/backend/Dockerfile` changes.
