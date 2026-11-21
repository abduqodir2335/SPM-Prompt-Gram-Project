# GitHub Copilot instructions

All project rules for AI agents are in [`AGENTS.md`](../AGENTS.md) at the repository root. Read it first and follow it. Do not duplicate its rules here.

Short reminder of the points that matter most:

- The documents in `docs/` are the specification. Read the ones that fit your task before you write code (`AGENTS.md` section 2 has the map).
- One issue = one branch = one pull request. Never push to `main`.
- Write tests from the acceptance criteria first. Run `make check` before you open the pull request.
- Never commit secrets. Never weaken or skip a check. Never touch production data.

Copilot specifics (nothing else belongs in this file):

- In agent mode, state your plan before you edit files.
- When you review a pull request, check it against `docs/01-requirements.md`, `docs/04-api.md` and `docs/07-security.md`.
