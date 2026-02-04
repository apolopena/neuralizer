---
description: Quick prime from existing context files
---

## Instructions
Read `CLAUDE.md` `.ai/TASKS.md`

1. **Read both files in parallel**: `.ai/scratch/arch-primer.md` and `.ai/scratch/context-primer.md`
   - If either file is missing, error and tell user to run `/prime-full` first
   - Also read recent entries from `CHANGELOG.md` if present
2. **Present 100-150 word synthesis** with emojis covering:
   - **One-line codebase purpose** (first line, before other sections):
     - Line 1: 3 emojis representing the project's core purpose (space-separated)
     - Line 2 (indented): The actual description
   - Architecture overview
   - Current work/branch status
   - Key patterns and workflows
   - Next steps
3. **End with**: "✅ Primed and ready to work!"

**CRITICAL**: 
- All steps MUST happen in ONE message. Read both files in parallel, then synthesize.
- Format results for human readability.
