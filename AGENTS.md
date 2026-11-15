# Bomu — agent instructions (Antigravity / any non-Claude agent)

`CLAUDE.md` in this folder is the single shared project log for ALL agents
(Claude Code and Antigravity). Follow it exactly.

1. **At session start:** read `CLAUDE.md` (especially the newest dated entries
   and the "Session handoff protocol" section) before doing anything.
2. **Before ending a session / when the user says "close sesh":** append a dated
   entry to `CLAUDE.md` covering what changed, decisions made, gotchas hit, and
   what is left to do. Never write secret values (passwords, API keys, DB URLs)
   — names only. Then commit and push it with the rest of the work.
3. Do not duplicate the log here; keep this file as a pointer only.
