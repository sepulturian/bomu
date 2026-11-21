# Bomu — agent instructions (Antigravity / any non-Claude agent)

`CLAUDE.md` in this folder is the shared project memory for ALL agents
(Claude Code and Antigravity): the current state, plus copies of the newest 2
session entries. The full dated history lives in `docs/session-log.md`.
Follow `CLAUDE.md` exactly.

1. **At session start:** read `CLAUDE.md` (especially "Where things stand",
   "Gotchas", "Recent sessions" and the "Session handoff protocol" section)
   before doing anything. Open `docs/session-log.md` only when you need history.
2. **Before ending a session / when the user says "close sesh":**
   - append a dated `### YYYY-MM-DD` entry to the **bottom** of
     `docs/session-log.md` covering what changed, decisions made, gotchas hit,
     and what is left to do;
   - refresh "Recent sessions" in `CLAUDE.md` so it holds copies of the newest
     2 entries;
   - update the current-state sections of `CLAUDE.md` (counts, hosting, schema,
     backlog, gotchas) in the present tense, and keep the file under ~30 KB.
   Never write secret values (passwords, API keys, DB URLs) — names only. Then
   commit and push `CLAUDE.md` and `docs/session-log.md` with the rest of the work.
3. Do not duplicate the log here; keep this file as a pointer only.
