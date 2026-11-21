# AGENTS.md — rules for AI coding agents

This file is the single source of rules for every AI agent in this repository (Claude Code, GitHub Copilot, Codex and others).
`CLAUDE.md` and `.github/copilot-instructions.md` only point here. Do not copy rules into them.

## 1. Project in one paragraph

PromptGram is a small social web app for sharing AI prompts. React SPA (`frontend/`) + Flask REST API (`backend/`) + PostgreSQL. Three containers run on a shared course server under one student's rootless Docker. GitHub Actions tests, builds and deploys every merge to `main`.

## 2. Source of truth

The documents in `docs/` are the specification. Code follows the documents.

| Question | Read |
|---|---|
| What must the product do? | `docs/01-requirements.md` |
| Which services, folders, config variables? | `docs/02-architecture.md` |
| Tables and migrations? | `docs/03-data-model.md` |
| Endpoints, payloads, errors? | `docs/04-api.md` |
| Workflows, deploy script, rollback? | `docs/05-cicd-and-deployment.md` |
| Which tests, where, how isolated? | `docs/06-testing.md` |
| Security rules? | `docs/07-security.md` |
| What is the next task? | `docs/09-plan.md` and `docs/STATUS.md` |
| Why was X chosen? | `docs/10-decisions.md` |

Rules for the documents:

1. Read the documents for your task **before** you write code. Do not load all of them; load the ones in the table that fit.
2. If the task needs behaviour that the documents do not describe, or that contradicts them, **stop and ask the human**. Then change the document in the same PR as the code.
3. A technology or architecture change needs a new entry in `docs/10-decisions.md`, approved by the human.
4. Update `docs/STATUS.md` in every PR that finishes a task.
5. **Versions are fixed** in `docs/02-architecture.md` section 10. Several are newer than your training data (React Router 8, Vite 8, Vitest 5, MSW 3, ESLint 10, SQLAlchemy 2.1, PostgreSQL 18, gunicorn 27). Read the list of known traps there before you scaffold. When an API differs from what you remember, read the official documentation of that version. Never downgrade a package to match your memory.

## 3. Hard rules (never break these)

1. **Never touch production by hand.** Do not SSH to the server to change the running app. Deployment happens only through the pipeline. Read-only inspection (`docker compose ps`, `logs`) is allowed when the human asks.
2. **Never run `docker compose down -v`, `docker volume rm` or `DROP DATABASE` against production.** Volumes hold user data.
3. **Never point tests at a database whose name does not end in `_test`.** Do not remove the guard in `backend/tests/conftest.py`.
4. **Never commit secrets.** No passwords, keys or tokens in code, `.env` files, workflow files, logs or PR text. `.env` files are git-ignored. Only `.env.example` templates with placeholder values are committed. `deploy/.env.example` is the template of the server file; the human creates the real file on the server.
5. **Never read or print** the human's private keys or the content of real `.env` files. Ask the human to do steps that need them.
6. **Never push to `main` directly, never force-push, never rewrite published history.** Work on a branch and open a PR.
7. **Never edit a migration file that is already merged to `main`.** Add a new migration.
8. **Never weaken a check to make it pass.** Do not delete or skip tests, lower coverage limits, add `# noqa` / `eslint-disable` / `@ts-ignore`, or set `continue-on-error` without the human's approval in the PR.
9. **Never add a dependency without need.** Before you add one: confirm that the package exists in the official registry, is maintained and is widely used. Say why in the PR. Lockfiles must be updated by the package manager, not by hand.
10. **Use only GitHub-owned actions** (`actions/*`, `github/*`). No third-party action, for any purpose. Everything else in a workflow is plain shell (`docker`, `ssh`, `scp`, `curl`). Pin every action to a full commit SHA. The list of allowed actions is in `docs/05-cicd-and-deployment.md` section 3.

## 4. Workflow for every task

1. Take one task (one GitHub issue). One task = one branch = one PR.
2. Branch name: `feat/<issue>-<slug>`, `fix/<issue>-<slug>`, `chore/<slug>`, `docs/<slug>`.
3. State a short plan first: files to change, tests to add. Wait for approval when the human works interactively.
4. Write or update tests from the acceptance criteria first. Then write the code.
5. Run the checks in section 6 locally. All must pass before you open the PR.
6. Open a PR with the template. PR title = Conventional Commit (`feat(posts): add like button`). Keep the diff under about 400 changed lines. Split larger work.
7. Do not merge. The human reviews and merges with **squash**.

## 5. Repository layout (target, created in Phase 1)

```
backend/            Flask app (app/, migrations/, tests/, pyproject.toml, uv.lock, Dockerfile)
frontend/           React app (src/, e2e/, package.json, package-lock.json, Dockerfile, nginx.conf)
deploy/             compose.yaml (production), deploy.sh, backup.sh, restore.sh
compose.dev.yaml    Local development stack
compose.e2e.yaml    End-to-end test stack (CI and local)
Makefile            Short aliases for the commands below
.github/workflows/  ci.yml, deploy.yml
docs/               Specification (source of truth)
```

When `backend/` and `frontend/` exist, each gets its own short `AGENTS.md` with folder-specific conventions. Those files must not repeat this one.

## 6. Commands

Phase 1 creates these commands with exactly these names. After Phase 1 they are the only supported way to run things.

| Purpose | Command |
|---|---|
| Start the dev stack (db, api with reload, Vite) | `make dev` → `docker compose -f compose.dev.yaml up --build` |
| Stop the dev stack (keeps dev data) | `make down` |
| Backend lint + format check | `make lint-backend` → `ruff check . && ruff format --check .` in `backend/` |
| Backend tests with coverage | `make test-backend` → `pytest` in the `api` dev container |
| Frontend lint + types | `make lint-frontend` → `npm run lint && npm run typecheck` |
| Frontend unit tests | `make test-frontend` → `npm test` |
| All of the four above | `make check` |
| End-to-end tests on built images | `make e2e` |
| Apply migrations (dev) | `make migrate` |
| Create a migration | `make migration m="add likes table"` |
| Format everything | `make fmt` |

App in development: `http://localhost:5173` (web), `http://localhost:8000` (api), PostgreSQL on `localhost:5432`.

## 7. Code conventions

**Backend (Python 3.14, Flask 3.1)**
- App factory `create_app()` in `backend/app/__init__.py`. One blueprint per resource in `app/api/`.
- Layers: `api/` (HTTP only) → `services/` (business rules) → `models/` (SQLAlchemy 2.1, typed `Mapped[...]`). No SQL in `api/`.
- Request and response bodies are Pydantic 2 models in `app/schemas/`. JSON uses `snake_case`.
- Errors use the one error format in `docs/04-api.md`. Raise typed exceptions; one handler converts them.
- Every endpoint that changes state needs: login, CSRF token, ownership check where it applies, and tests for 401, 403 and 422.
- Config only from environment variables (`app/config.py`). No defaults for secrets.
- Format and lint with Ruff. Type hints on all public functions.

**Frontend (React 19, TypeScript 6 strict)**
- Function components and hooks only. Pages in `src/pages/`, shared UI in `src/components/`, API calls in `src/api/` (one typed client, no `fetch` in components).
- Server state with TanStack Query. No global state library.
- Always call the API with relative URLs (`/api/v1/...`). Never hard-code a host or port.
- Tailwind utility classes. No inline styles, no CSS frameworks added on top.
- Every interactive element is reachable by keyboard and has an accessible name.
- Render user text as text. Never use `dangerouslySetInnerHTML`.

**Both**
- English for code, comments, commits and docs.
- Comments explain *why*, not *what*.
- Docs: short sentences, active voice, one instruction per sentence.

## 8. Definition of done

A task is done when all of these are true:

- [ ] The acceptance criteria of the story pass, proven by automated tests.
- [ ] `make check` passes locally. CI is green on the PR.
- [ ] New behaviour has tests: backend unit/integration, frontend component tests, and an e2e step when the user flow changed.
- [ ] No secret, debug output or dead code in the diff.
- [ ] Documents and `docs/STATUS.md` are updated in the same PR.
- [ ] The PR description says what changed, how it was tested, and which AI tool helped.
- [ ] After merge: the pipeline deployed it and `http://spm.iotserver.uz:<PORT>/api/health` shows the new commit SHA. (A change of documents only is not built or deployed; the version stays the same.)

## 9. When you are not sure

Ask the human one clear question with 2–3 options and your recommendation. Do not guess requirements. Do not invent endpoints, fields or config variables that are not in `docs/`.
