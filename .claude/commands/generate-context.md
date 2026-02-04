---
description: Generate/update .ai/scratch/context-primer.md with current working state
---

**Generate new context**

## Step 1: Read Available Documentation
Read `.ai/docs/README.md` to understand what documentation is available for context.

## Step 2: Run Git Commands
- `git branch --show-current`
- `git log -5 --oneline` (5 commits max)
- `git status --short` (counts only, don't list every file)
- `git diff --cached --stat` (stat line only, don't analyze content)

## Step 3: Read Work Ledger and CHANGELOG
Read `.ai/TASKS.md` to get complete list of all completed work (Done section).
Then read from `CHANGELOG.md` - whichever provides MORE context:
- Last 3 version sections, OR
- Last 100 commit entries
Choose whichever gives more comprehensive information about recent progress.

**CRITICAL:** TASKS.md is the source of truth for all completed work. CHANGELOG.md is only updated at release time. Always prioritize TASKS.md for recent work.

## Step 4: Generate Context File

```markdown
# Branch Context: <branch-name>

## Goal
<1 sentence from branch name>

## Code Standards

### Datetime Handling
**CRITICAL:** Never use `datetime.utcnow()` or naive `datetime.fromisoformat()`.

```python
# ALWAYS use these wrappers from utils/datetime_utils.py:
from utils.datetime_utils import utcnow, parse_iso_utc

# Getting current time
now = utcnow()  # NOT datetime.now(timezone.utc)

# Parsing timestamps from database
expires_at = parse_iso_utc(session["expires_at"])  # NOT datetime.fromisoformat()
```

**Why:** Handles both naive (legacy dev data) and timezone-aware timestamps. Prevents "can't compare offset-naive and offset-aware datetimes" crashes.

## Recent Work (from TASKS.md)
- <All completed items from TASKS.md Done section, especially POST-IMPL-* items>

## Release History (from CHANGELOG)
- <Summary from last 3 version sections OR last 100 commit entries, whichever is more comprehensive>

## Progress
- [x] <Completed items from commits>
- [ ] <In-progress from staged files>

## Next Steps
- <Next items to work on>

## Notes
<Blockers or critical info only>
```

Analyze git state, TASKS.md (primary source), CHANGELOG, and available docs, then create/update `.ai/scratch/context-primer.md`.

## Rules

- File path: `.ai/scratch/context-primer.md`
- Always overwrite file
- **Target ~300 lines (hard max 400)** - comprehensive but focused
- Use checkboxes: [x] done, [ ] pending
- **CRITICAL: DO NOT read any files in `.ai/scratch/` except the output file itself**
- **CRITICAL: DO NOT use Glob or Grep on gitignored directories (use `git ls-files` to find tracked files only)**
