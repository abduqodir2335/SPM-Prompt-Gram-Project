# 10 — Decision log

Each entry records one decision: the context, the choice, the alternatives and the consequences. Add a new entry when you change technology, architecture or a rule. Never rewrite an old entry: add a new one that replaces it and mark the old one "Replaced by D-nn".

Template:

```
## D-nn — Title
- Date / Status: YYYY-MM-DD / Accepted | Replaced by D-nn
- Context: the problem and the forces
- Decision: what we do
- Alternatives: what we did not choose and why
- Consequences: what becomes easier, what becomes harder
```

Version rule for all entries: the versions to use are in `docs/02-architecture.md` section 10 (decision D-23). Older entries below may name earlier version numbers; section 10 wins. Phase 1 records the exact versions in the lockfiles. Dependabot moves them afterwards.

---

## D-01 — Single-page app + REST API + PostgreSQL, same origin
- Date / Status: 2026-11-14 / Accepted
- Context: The brief fixes React, Flask and PostgreSQL. The app sits behind a login.
- Decision: React SPA, Flask JSON API under `/api`, both served through one nginx on one port. No CORS.
- Alternatives: Flask server-rendered templates (no React, against the brief). Separate ports for web and API (needs CORS and cross-site cookies; breaks on HTTP).
- Consequences: Simple cookie authentication. One public port per student.

## D-02 — Frontend stack: React 19, TypeScript, Vite, React Router 7, TanStack Query 5, Tailwind 4
- Date / Status: 2026-11-14 / Accepted. The **versions** are replaced by D-23 (React Router 8, Vite 8, TypeScript 6, Node.js 26).
- Context: Need fast feedback for humans and agents, and little hand-written plumbing.
- Decision: As titled. npm as package manager. Node 24 LTS.
- Alternatives: Next.js (server rendering not needed, larger image, second server process). Plain JavaScript (fewer checks; agents make more unnoticed mistakes). Redux (no global client state to manage). Component libraries such as MUI (bigger bundle, style lock-in).
- Consequences: Static build served by nginx; tiny runtime image. Types catch contract drift between frontend and API.

## D-03 — Backend stack: Python 3.14, Flask 3.1, SQLAlchemy 2, Flask-Migrate, psycopg 3, Pydantic 2, gunicorn
- Date / Status: 2026-11-14 / Accepted. The **versions** are replaced by D-23 (SQLAlchemy 2.1, gunicorn 27 with one worker).
- Context: Flask is fixed by the brief. The rest must be mainstream so that every AI tool knows it well.
- Decision: As titled. App factory, blueprints, service layer.
- Alternatives: FastAPI (not the brief). Marshmallow for validation (works; Pydantic gives typed models and clearer errors). Raw SQL (more code, easier to make injection mistakes). Flask-RESTX / automatic OpenAPI (extra layer; the contract in 04 is small).
- Consequences: Clear layers that are easy to test. Migrations are files that the pipeline applies.

## D-04 — PostgreSQL 17, official alpine image
- Date / Status: 2026-11-14 / **Replaced by D-23** (PostgreSQL 18)
- Context: PostgreSQL is fixed by the brief. Newer major versions exist. The disk quota is small.
- Decision: `postgres:17-alpine`, pinned by digest, data in a named volume at `/var/lib/postgresql/data`.
- Alternatives: PostgreSQL 18 or newer (the official image changed its data directory layout from 18 on; most guides and AI answers still describe the old path, which risks a silent "data not in the volume" mistake). SQLite (not the brief). A managed database (no budget, no need).
- Consequences: Supported until November 2029. A major upgrade later needs dump and restore.

## D-05 — Session cookie authentication with CSRF tokens, not JWT
- Date / Status: 2026-11-14 / Accepted
- Context: SPA and API share an origin. The server is HTTP only and all students share one host name.
- Decision: Flask-Login signed session cookie (`HttpOnly`, `SameSite=Lax`, unique name per port) + Flask-WTF CSRF header token. Passwords hashed with scrypt (Werkzeug).
- Alternatives: JWT in `localStorage` (readable by any script; no real logout; more code). JWT in a cookie (same CSRF needs, more parts). Argon2 (also good; one more native dependency). OAuth login (out of scope).
- Consequences: Little code, good defaults. Limits L-1 to L-3 in 07.

## D-06 — Uploaded files on a Docker volume, served by the API
- Date / Status: 2026-11-14 / Accepted
- Context: Posts have attachments. Files must be visible only to members. Disk and RAM are scarce.
- Decision: Store files in the `uploads` volume with random names; metadata in PostgreSQL; serve through `/api/v1/media/{id}` after a login check. Strict allow-list and size limits.
- Alternatives: Files in the database (bloats backups, slow). MinIO / S3 (another container, about 100 MB RAM and more disk). nginx serving the volume directly (fast, but no login check without extra configuration).
- Consequences: Simple and private. The API process streams files, which is fine at class scale.

## D-07 — Two-step post creation: JSON post, then one upload per file
- Date / Status: 2026-11-14 / Accepted
- Context: A post can have up to four files.
- Decision: `POST /posts` with JSON, then `POST /posts/{id}/attachments` per file.
- Alternatives: One multipart request with all fields and files (one failure loses everything; harder validation errors; no per-file progress).
- Consequences: Posts and attachments ship in different phases. A failed upload does not lose the text.

## D-08 — Docker Compose on rootless Docker; three containers
- Date / Status: 2026-11-14 / Accepted
- Context: The server gives each student a rootless Docker daemon, a 3 GB quota and 50 ports.
- Decision: One compose project `promptgram` with `web`, `api`, `db`; two named volumes; limits per container; only `web` published.
- Alternatives: Kubernetes or Swarm (far too heavy). One container with everything (no separation, hard to update). Running without containers (against the goal; needs sudo).
- Consequences: Whole stack in one file. Each student is isolated by their own daemon.

## D-09 — Images in GHCR, tagged with the commit SHA
- Date / Status: 2026-11-14 / Accepted
- Context: The server must not hold source code or build tools. Deployments must be repeatable.
- Decision: CI builds images, pushes to `ghcr.io/<owner>/<repo>/{api,web}:<sha>` (private). The server pulls by SHA.
- Alternatives: Build on the server (needs source and build tools there; fills the quota; slow on 2 shared CPUs). Docker Hub (extra account, pull limits, private repository limits). `latest` tag (not repeatable, no rollback).
- Consequences: Any commit of `main` can be deployed again. Old images stay in GHCR until cleaned.

## D-10 — Push-based deployment over SSH from GitHub-hosted runners
- Date / Status: 2026-11-14 / Accepted
- Context: Deployment must be automatic and give a clear pass or fail in the pipeline.
- Decision: `deploy.yml` connects with a dedicated SSH key, copies `compose.yaml` and `deploy.sh`, runs the script, verifies health from outside. Plain `ssh`/`scp`, no third-party SSH action. Host key pinned.
- Alternatives: Self-hosted runner in the student account (uses shared CPU, RAM and quota; a permanent agent with repository access on a shared machine). Pull-based tools such as Watchtower or a cron job (no deployment result in the pipeline, no migrations step, needs a long-lived registry token on the server). Third-party SSH actions (a private key handed to code we do not control).
- Consequences: One secret to manage (limit L-8). The pipeline shows the real result of each deployment.

## D-11 — Short-lived `GITHUB_TOKEN` for image pulls on the server
- Date / Status: 2026-11-14 / Accepted
- Context: GHCR images are private. The server needs credentials only during a deployment.
- Decision: The deploy job pipes its `GITHUB_TOKEN` to `docker login` on the server through stdin; the script logs out after the pull.
- Alternatives: Personal access token stored on the server (long-lived secret on a shared machine; expires and breaks deployments). Public images (the course repositories are private).
- Consequences: Nothing to rotate. Containers restart from local images, so no registry access is needed between deployments.

## D-12 — Server secrets are generated on the server
- Date / Status: 2026-11-14 / **Replaced by D-22**
- Context: The database password and `SECRET_KEY` must exist only in production.
- Decision: `deploy.sh` creates `~/promptgram/.env` on the first run with `openssl rand`. They never go to GitHub or to a developer machine.
- Alternatives: GitHub secrets written to the server on each deployment (more copies of each secret; visible to workflow changes).
- Consequences: Zero manual secret handling for students. The values are lost if the file is deleted: then the sessions end and the database password must be reset.

## D-13 — One workflow for checks, one reusable workflow for deployment
- Date / Status: 2026-11-14 / Accepted
- Context: We need gates before deploy and a manual rollback.
- Decision: `ci.yml` (jobs `backend`, `frontend`, `image`, `deploy`) calls `deploy.yml`, which can also run by hand with an `image_tag`.
- Alternatives: `workflow_run` chaining (runs on the default branch context, harder to reason about, weaker link between commit and deployment). One huge workflow file (no manual rollback entry point).
- Consequences: Build once; the tested image is the deployed image. Rollback uses the same code path as deployment.

## D-14 — Migrations run as a separate step, forward-only and backward compatible
- Date / Status: 2026-11-14 / Accepted
- Context: Automatic rollback restarts old containers. gunicorn has several workers.
- Decision: `deploy.sh` runs `flask db upgrade` once before the rollout. Migrations must work with the previous code release. A pre-deploy dump is the safety net.
- Alternatives: Migrate at container start (workers race; a failed migration loops the container). Automatic `downgrade` on rollback (can destroy data).
- Consequences: Column removals take two releases. Students learn expand/contract.

## D-15 — Tests on real PostgreSQL in a separate database with a hard guard
- Date / Status: 2026-11-14 / Accepted
- Context: "When doing tests, do not alter main data."
- Decision: Database `promptgram_test`; a guard in `conftest.py` stops the run for any other name; CI uses a service container; e2e uses a temporary stack; the post-deploy check is read-only.
- Alternatives: SQLite for tests (different SQL behaviour: `ON CONFLICT`, row locks, constraints). Mocked database (tests prove little).
- Consequences: Tests need Docker. They are a bit slower and far more honest.

## D-16 — Tooling: uv + Ruff + pytest; ESLint + Prettier + Vitest; Playwright; Trivy; Dependabot
- Date / Status: 2026-11-14 / Accepted. The Trivy part is **replaced by D-21** (GitHub's own security tools instead).
- Context: Checks must be fast, free for private repositories, and well known to AI tools.
- Decision: As titled.
- Alternatives: pip + requirements files (no real lockfile). Poetry (slower; fine otherwise). Black + Flake8 + isort (three tools instead of one). Jest (slower with Vite). Cypress (heavier; weaker multi-user tests).
- Consequences: One command per side. Security scanning: see D-21.

## D-17 — One `AGENTS.md` as the source of agent rules
- Date / Status: 2026-11-14 / Accepted
- Context: Students use Claude Code, GitHub Copilot or Codex. Rules must not diverge.
- Decision: Rules live in `AGENTS.md`. `CLAUDE.md` imports it. `.github/copilot-instructions.md` points to it. Specification lives in `docs/`. Progress lives in `docs/STATUS.md`.
- Alternatives: One full rule file per tool (three copies drift apart). Tool-specific prompt or command folders (not portable).
- Consequences: A rule is written once. Tool-specific files stay under ten lines.

## D-18 — GitHub Flow with squash merges and Conventional Commits
- Date / Status: 2026-11-14 / Accepted
- Context: One student per repository; every merge deploys.
- Decision: Short-lived branches from `main`, PR required, required checks, squash merge, PR title in Conventional Commit form. Tags `v0.N.0` per phase, `v1.0.0` at release.
- Alternatives: Git Flow with `develop` and release branches (overhead without benefit for continuous deployment). Direct pushes to `main` (no gate, no review).
- Consequences: Linear history; one commit per task; easy revert.

## D-19 — Development and tests do not run on the SPM server
- Date / Status: 2026-11-14 / Accepted
- Context: The server has 2 CPUs, 7.7 GB RAM and a 3 GB quota per student.
- Decision: Develop on your own computer (Docker Desktop or WSL 2) or in a GitHub Codespace. CI runs on GitHub-hosted runners. The server runs production only.
- Alternatives: Remote development on the server (Node images and `node_modules` alone exceed the quota; builds starve other students).
- Consequences: The server stays fast and clean. Students need Docker locally or a Codespace.

## D-20 — No separate staging environment
- Date / Status: 2026-11-14 / Accepted
- Context: A staging stack per student would double disk and memory use on the shared server.
- Decision: The e2e stack in CI (the real images, a temporary database) is the pre-production check. Ports `PORT_BASE+1…+9` are reserved if staging is added later.
- Alternatives: Staging on the server (resources). Preview deployments per PR (same problem, more so).
- Consequences: Server-specific problems (rootless Docker, quota) show up only in production deployment. The health-gated rollout with automatic return to the previous release covers this risk.

## D-21 — GitHub-owned actions and GitHub's own tools only
- Date / Status: 2026-11-14 / Accepted. Replaces the Trivy part of D-16 and the action list first written for D-13.
- Context: Course requirement from the teacher: students and the project use GitHub's tools for CI and CD, not third parties. The first draft used third-party actions for uv, Docker build and push, and Trivy.
- Decision: Workflows use only actions owned by GitHub (`actions/*`, `github/*`), pinned to commit SHAs. All other steps are plain shell with the tools that GitHub-hosted runners already have (`docker`, `ssh`, `curl`) or that a package manager installs (`pip install uv`). The repository setting *Allow actions created by GitHub* enforces it. Security checks use GitHub features: Dependabot always; secret scanning, push protection and CodeQL when the organisation is licensed for private repositories. Planning, review, registry, environments and releases also use GitHub features (README section 5).
- Alternatives: Verified third-party actions such as `docker/build-push-action`, `astral-sh/setup-uv`, `aquasecurity/trivy-action` (convenient, but each one is outside code that runs with the job's token, and against the course rule). Another CI service (against the rule).
- Consequences: Smaller supply-chain surface: no third-party code runs in the pipeline with access to tokens. Students see the real `docker` commands. Costs: no Docker layer cache in the first version (builds take 2–3 minutes); no container image vulnerability scan (GitHub has none; official base images pinned by digest and updated by Dependabot reduce the risk); without the paid licence there is no automatic secret or code scanning on private repositories, so review carries that weight.

## D-22 — The student creates the server `.env` from a committed template
- Date / Status: 2026-11-14 / Accepted. Replaces D-12.
- Context: Course requirement from the teacher: the repository has a `.env` template, and each student copies it to the server and puts in their own credentials. Handling configuration and secrets by hand, once, is a learning goal.
- Decision: `deploy/.env.example` is committed with placeholders. The student copies it to `~/promptgram/.env` on the server, fills in `POSTGRES_PASSWORD` and `SECRET_KEY`, and sets mode `600` (STUDENT-GUIDE step 0.5). `deploy.sh` checks the file and refuses to deploy when it is missing or still has `CHANGE_ME`. The pipeline rewrites only `IMAGE_REPO`, `IMAGE_TAG` and `WEB_PORT`.
- Alternatives: The script generates the secrets (D-12: no manual step, but the student never sees how configuration works). GitHub secrets written to the server on each deployment (more copies of each secret).
- Consequences: One more manual step before the first deployment. Students own their credentials and can read the configuration in one place. Risks: weak values, or a real `.env` committed by mistake. Controls: the template shows how to make random values; `.gitignore` blocks `.env`; `deploy.sh` rejects placeholders and short keys; push protection where licensed.

## D-23 — Version baseline checked and updated (PostgreSQL 18, Node.js 26, current package majors)
- Date / Status: 2026-11-14 / Accepted. Replaces D-04 and the version numbers in D-02 and D-03.
- Context: The first version list came from memory. A check against the registries on 2026-11-14 showed that parts of it were behind: Node.js 26 had become the active LTS, React Router was at 8, Vite at 8, Vitest at 5, MSW at 3, ESLint at 10, SQLAlchemy at 2.1, gunicorn at 27, and PostgreSQL 18 was the current major release. TypeScript 7 was the newest TypeScript, but `typescript-eslint` did not support it.
- Decision: Use the versions in `docs/02-architecture.md` section 10. Rule for choosing: the newest stable release line that every other chosen tool supports, and for runtimes a line that is at least some months old (Python 3.14, not 3.15). PostgreSQL 18 with the volume at `/var/lib/postgresql`. TypeScript stays at 6.0 until the lint tool supports 7. gunicorn runs one worker with eight threads.
- Evidence: one test run with exactly these versions on a GitHub-hosted runner (what it covered: 02 section 10.4). The reason for D-04 (fear of silent data loss with the new PostgreSQL 18 data path) did not hold: the image stops with a clear error when the old path is mounted.
- Alternatives: Stay on the older lines (PostgreSQL 17, Node.js 24, React Router 7: all still supported, but students would start a new project on yesterday's versions and meet upgrade work early). Take the newest of everything (Python 3.15, TypeScript 7: too new, tool support incomplete).
- Consequences: The stack is current and proven to install, lint, test, build and run together. Several APIs are newer than what AI tools remember; section 10.5 lists the traps, and `AGENTS.md` tells agents to read it. Dependabot keeps the versions moving; the TypeScript major is held back by an ignore rule.

## D-24 — A change of documents only is not built and not deployed
- Date / Status: 2026-11-14 / Accepted. Refines D-13.
- Context: Every merge to `main` ran the full pipeline and redeployed, also when only `docs/` or a `*.md` file changed. That costs 6–10 runner minutes and restarts the containers for nothing. This project changes documents often.
- Decision: A first job `changes` decides, with plain `git diff`, whether a non-document file changed. `backend`, `frontend`, `image` and `deploy` run only then. The workflow itself always starts, so the required checks always report. `changes` is a required check too.
- Alternatives: `paths` filters on the workflow trigger (a workflow that does not start leaves required checks pending for ever, and the pull request cannot merge). Always run everything (simple, wasteful). A third-party "paths filter" action (against D-21).
- Consequences: `/api/health` shows the newest **code** commit, which can be older than the head of `main`. Images exist only for code commits. If the `changes` logic has a bug, the fail-safe is to run everything.

## D-25 — `main` is protected from day one; Windows students work in WSL 2 from VS Code
- Date / Status: 2026-11-14 / Accepted. Refines D-18 and D-19.
- Context: The ruleset was created only after the first green pipeline, so in Phase 0 and most of Phase 1 a direct push to `main` was possible. Most students use Windows and VS Code; the guide gave bash commands without saying where to type them.
- Decision: The ruleset `protect-main` (pull request required, no force push, no deletion, linear history, squash only) is created in Phase 0. The required status checks are added at the end of Phase 1, because GitHub knows a check name only after its first run. The supported setup on Windows is WSL 2 (Ubuntu) + Docker Desktop with WSL integration + VS Code with the WSL extension; every command is typed in the Ubuntu terminal. macOS uses its normal terminal. Repository names are free.
- Alternatives: Protect `main` only when the checks exist (leaves a gap). PowerShell versions of all commands (two command sets to maintain; `make` and the shell scripts still need bash). Git Bash on Windows (no Docker integration, no `make`).
- Consequences: Even the first scaffolding goes through pull requests. Until the end of Phase 1 a pull request can be merged with red checks; the student guide warns about it. One command set for all students.

