# 09 — Plan: phases, tasks, exit criteria

The project has seven phases. Each phase ends with a working, deployed product and a Git tag. Do the phases in order. Do the tasks inside a phase in order, unless a task says otherwise.

- Each task becomes one GitHub issue and one pull request.
- Task IDs (`P1-T3`) are stable. Use them in issue titles and in `docs/STATUS.md`.
- Manual steps for the human are in [STUDENT-GUIDE.md](STUDENT-GUIDE.md). Prompts are in [prompts.md](prompts.md).
- Size: S = under 1 hour with an AI agent, M = 1–3 hours, L = half a day. Includes review.

| Phase | Result | Tag | Suggested time |
|---|---|---|---|
| 0 | Repository, access and backlog ready | — | Week 1 |
| 1 | Walking skeleton live on the server through the pipeline | `v0.1.0` | Week 1–2 |
| 2 | Authentication | `v0.2.0` | Week 2 |
| 3 | Posts, feed, profile | `v0.3.0` | Week 3 |
| 4 | Attachments | `v0.4.0` | Week 4 |
| 5 | Likes and comments | `v0.5.0` | Week 4–5 |
| 6 | Hardening and release | `v1.0.0` | Week 5–6 |

---

## Phase 0 — Setup (human work)

**Goal:** everything that an AI agent cannot do for you is done.

| ID | Task | Who |
|---|---|---|
| P0-T1 | Install tools; create the repository from the template | Human |
| P0-T2 | Check the server account and rootless Docker | Human |
| P0-T3 | Create the deployment SSH key; install the public key on the server | Human |
| P0-T4 | Create the server `.env` from `deploy/.env.example` with your own credentials | Human |
| P0-T5 | Create GitHub environment `production` with secret and variables | Human |
| P0-T6 | Set the repository settings (Actions policy, merge method, Dependabot, **ruleset `protect-main`: pull request required**); connect your AI tool | Human |
| P0-T7 | Create labels, milestones and issues from this plan; put them on a GitHub Projects board | Agent (prompt "Create the backlog") + Human |

**Exit criteria**
- [ ] `ssh -i <deploy key> <user>@spm.iotserver.uz docker ps` works from your computer.
- [ ] On the server, `~/promptgram/.env` exists with mode `600` and has no `CHANGE_ME` (`grep -c CHANGE_ME ~/promptgram/.env` prints `0`).
- [ ] Environment `production` has 1 secret and 4 variables.
- [ ] Your agent answers "What are the hard rules of this repository?" correctly (it found `AGENTS.md`).
- [ ] Issues exist for Phase 1 at least, and they are on the Projects board.
- [ ] Repository Actions policy is *Allow actions created by GitHub* only. Dependabot alerts and security updates are on.
- [ ] A direct `git push origin main` is rejected (ruleset `protect-main`).

---

## Phase 1 — Walking skeleton + CI/CD

**Goal:** the thinnest possible product goes through the complete pipeline to the server. A page says "PromptGram" and shows the API status and version. No features.

**Why first:** deployment problems appear on day one, not on the last day. Every later phase ships automatically.

| ID | Task | Size | Done when |
|---|---|---|---|
| P1-T1 | **Backend skeleton.** Versions from 02 section 10.2. `backend/` with uv, Flask app factory, config from env, JSON logging, error handler, `GET /api/health` (with DB check), SQLAlchemy + Flask-Migrate set up with an empty first migration, pytest with the `_test` guard and its test, Ruff config, `backend/AGENTS.md`. | M | `pytest` green; health test passes; guard test passes |
| P1-T2 | **Frontend skeleton.** Versions from 02 section 10.3; read the traps in 10.5 first. `frontend/` with Vite, React, TypeScript strict, Tailwind, React Router, TanStack Query, ESLint + Prettier, Vitest + Testing Library + MSW. One page that calls `/api/health` and shows status and version. `frontend/AGENTS.md`. | M | `npm run lint`, `typecheck`, `test`, `build` green |
| P1-T3 | **Dev stack.** `compose.dev.yaml` (db with init script that creates `promptgram_test`, api with reload, web with Vite proxy for `/api`), `Makefile` with the commands of `AGENTS.md` section 6, `.env.example`, `.dockerignore` files. | M | `make dev` shows the page at `localhost:5173`; `make check` green |
| P1-T4 | **Production images.** Base images from 02 section 10.1. `backend/Dockerfile` and `frontend/Dockerfile` (multi-stage, non-root, `APP_VERSION` build-arg), `frontend/nginx.conf` per 02 and 07. `compose.e2e.yaml`. First Playwright test (Phase 1 scenario). | M | `make e2e` green locally; api image < 250 MB, web image < 80 MB |
| P1-T5 | **CI workflow.** `.github/workflows/ci.yml` with jobs `changes`, `backend`, `frontend`, `image` per 05 (no push, no deploy yet), **GitHub-owned actions only**, each pinned to a commit SHA. `.github/dependabot.yml`. | M | All three jobs green on the PR; `grep -rhE '^\s*-?\s*uses:' .github/workflows` shows only `actions/…` or `github/…` |
| P1-T6 | **Deployment.** `deploy/compose.yaml`, `deploy/deploy.sh` (with the `.env` checks of 05 section 5), `.github/workflows/deploy.yml`; keep `deploy/.env.example` and 02 section 6.2 in step with `compose.yaml`; `ci.yml` pushes images on `main` and calls deploy. | L | Merge → the page is live at `http://spm.iotserver.uz:<PORT>`; health shows the merged SHA |
| P1-T7 | **Backup and restore scripts.** `deploy/backup.sh`, `deploy/restore.sh` per 05. | S | Scripts pass `shellcheck`; tried once on the dev stack |
| P1-T8 | **Required checks on `main`.** Add `changes`, `backend`, `frontend`, `image` to the ruleset `protect-main` (human step, STUDENT-GUIDE 1.3). | S | A pull request with a red check cannot be merged |

Order: T1 and T2 can go in parallel. Then T3, T4, T5, T6. T7 and T8 last.

**Exit criteria**
- [ ] `http://spm.iotserver.uz:<PORT>` shows the page. `/api/health` returns `status: ok` and the SHA of the last merge.
- [ ] A second trivial PR (for example a text change) reaches the server with **no manual step**.
- [ ] Persistence check: on the server, `docker volume inspect promptgram_pgdata promptgram_uploads --format '{{.Name}} {{.CreatedAt}}'` shows the same creation time before and after the second deployment.
- [ ] Rollback check: run the `deploy` workflow by hand with the previous SHA. The page shows the old version. Deploy the newest again.
- [ ] On the server `~/promptgram/` contains only `compose.yaml`, `deploy.sh`, `.env`, lock, log and `backups/`. No source code.
- [ ] `quota -s` on the server shows less than 1.2 GB used.
- [ ] `main` is protected: pull request required and the four checks required.
- [ ] A documents-only pull request merges without a build and without a deployment.
- [ ] Every action in the workflows is GitHub-owned and pinned to a commit SHA.
- [ ] Tag `v0.1.0`.

---

## Phase 2 — Authentication

**Stories:** FR-01, FR-02, FR-03, FR-04. **API:** Auth section of 04.

| ID | Task | Size | Done when |
|---|---|---|---|
| P2-T1 | **User model + migration.** `users` table per 03. Password hashing helpers. | S | Migration up/down green; unit tests |
| P2-T2 | **Auth API.** `csrf`, `register`, `login`, `logout`, `me`; Flask-Login, Flask-WTF CSRF, Flask-Limiter; session cookie settings from config. | M | Integration tests for every AC of FR-01..03 on the API level, plus CSRF and 429 |
| P2-T3 | **Frontend API client + auth state.** `src/api/client.ts` (CSRF handling, error mapping), `useAuth`, route guard with `next` redirect. | M | Component tests with MSW |
| P2-T4 | **Login and register pages, header.** Forms with field errors, HTTP warning text on the register page (limit L-1), header with username and log out. | M | Component tests; a11y: labels, keyboard |
| P2-T5 | **e2e: auth journey.** Phase 2 scenario of 06. | S | Green in CI |

**Exit criteria**
- [ ] On the server: register, log out, log in, reload — all work.
- [ ] The account still exists after the next deployment (persistence).
- [ ] All ACs of FR-01..04 map to named tests.
- [ ] Tag `v0.2.0`.

---

## Phase 3 — Posts, feed, profile

**Stories:** FR-05, FR-06, FR-07, FR-08, FR-13. **API:** Posts and Users sections of 04.

| ID | Task | Size | Done when |
|---|---|---|---|
| P3-T1 | **Post model + migration.** `posts` table and indexes per 03. | S | Migration up/down green |
| P3-T2 | **Posts API: create, get, list with cursor paging.** Counts and `liked_by_me` return `0` / `false` for now but exist in the response. | M | Integration tests incl. paging over 45 posts, bad cursor, limits |
| P3-T3 | **Posts API: edit, delete, ownership.** Users API `GET /users/{username}`, `author` filter. | M | Tests for 403, 404, cascade |
| P3-T4 | **Feed page.** Post card, infinite scroll with "Load more", empty, loading and error states. | M | Component tests |
| P3-T5 | **Create and edit post pages.** Form validation, redirect to detail. | M | Component tests |
| P3-T6 | **Post detail page.** Prompt block, **Copy prompt**, edit/delete for the author, not-found page. | M | Component tests (clipboard mocked) |
| P3-T7 | **Profile page.** | S | Component tests |
| P3-T8 | **e2e: post journey.** Phase 3 scenario. `flask seed-demo` command for dev data. | S | Green in CI |

**Exit criteria**
- [ ] On the server: two accounts; each creates posts; feed shows both; only the author can edit or delete.
- [ ] Copy prompt works in the browser.
- [ ] Tag `v0.3.0`.

---

## Phase 4 — Attachments

**Stories:** FR-09. **API:** Attachments section of 04. **Security:** file upload rules of 07.

| ID | Task | Size | Done when |
|---|---|---|---|
| P4-T1 | **Attachment model + migration + storage service.** Random names, date folders, delete after commit, type detection by content. | M | Unit tests for every allowed and rejected type |
| P4-T2 | **Attachments API.** Upload, delete, `media` endpoint with headers; post delete removes files; 4-file limit. | M | Integration tests incl. 413, 415, 409, 403, headers |
| P4-T3 | **Frontend: file input in the post form.** Client-side checks (type, size, count) as a convenience, upload after post creation, per-file progress and error, remove file on edit. | M | Component tests |
| P4-T4 | **Frontend: show attachments.** Images in detail and first image in the card (lazy loading, fixed aspect box to avoid layout jumps), download links for files. | S | Component tests |
| P4-T5 | **e2e: attachment journey.** Phase 4 scenario. | S | Green in CI |

**Exit criteria**
- [ ] On the server: a post with an image and a text file; both still there after the next deployment.
- [ ] Opening a media URL in a private browser window (not logged in) gives 401.
- [ ] `quota -s` checked; uploads counted.
- [ ] Tag `v0.4.0`.

---

## Phase 5 — Likes and comments

**Stories:** FR-10, FR-11, FR-12. **API:** Likes and Comments sections of 04.

| ID | Task | Size | Done when |
|---|---|---|---|
| P5-T1 | **Like model + migration + API.** Idempotent PUT/DELETE; real `like_count` and `liked_by_me` in post responses without N+1 queries. | M | Integration tests incl. repeated requests; query-count test for the feed |
| P5-T2 | **Comment model + migration + API.** List (oldest first, paged), create, delete own; real `comment_count`. | M | Integration tests incl. 403 and rate limit |
| P5-T3 | **Like button.** Optimistic update with rollback on error, in card and detail. | S | Component tests |
| P5-T4 | **Comments UI.** List, load more, add, delete own with confirmation. | M | Component tests |
| P5-T5 | **e2e: social journey.** Phase 5 scenario with two users. | S | Green in CI |

**Exit criteria**
- [ ] On the server: two accounts like and comment on each other's posts; counts are right after reload.
- [ ] Tag `v0.5.0`.

---

## Phase 6 — Hardening and release

**Goal:** the product is safe enough, documented, and proven recoverable.

| ID | Task | Size | Done when |
|---|---|---|---|
| P6-T1 | **Security review.** Checklist of 07 section 6; independent AI review; fix findings. | M | Checklist complete in the PR; findings fixed or recorded as limits |
| P6-T2 | **Accessibility and responsive pass.** axe checks in e2e; mobile viewport test; keyboard-only run. | M | NFR-08, NFR-09 checks green |
| P6-T3 | **Performance check.** Seed 1000 posts in the **dev** stack; measure the feed API; fix N+1 or add an index if p95 > 300 ms. | S | Result written in the PR |
| P6-T4 | **Restore drill (human).** Manual backup on the server, download it, restore it into the **dev** stack on your computer, check the data. Then practise `restore.sh` on the dev stack. | M | Short report in `docs/STATUS.md` (date, backup size, result) |
| P6-T5 | **Documentation.** Update README (screenshots, live URL, how to run), check that all docs match the code, write `CHANGELOG.md`. | S | A new reader can run the dev stack from the README alone |
| P6-T6 | **Release.** Tag `v1.0.0`, GitHub Release with notes, final deployment verified. | S | Release exists; server shows the tagged SHA |

**Exit criteria**
- [ ] All stories FR-01..FR-13 work on the server.
- [ ] All NFR checks done.
- [ ] No open Dependabot alert with a fix; pipeline green.
- [ ] Restore drill report present.
- [ ] Tag `v1.0.0` and a GitHub Release.
- [ ] You can answer the five questions of 08 section 10.

---

## Stretch (only after v1.0.0)

Take items from the stretch backlog in 01 section 5, in order. Each needs: an update of 01 and 04 first, a decision record if it adds technology, then the normal task loop.

## Milestone summary for GitHub

Create one GitHub milestone per phase: `Phase 1 – Skeleton + CI/CD`, `Phase 2 – Auth`, `Phase 3 – Posts`, `Phase 4 – Attachments`, `Phase 5 – Social`, `Phase 6 – Release`. Labels: `phase-1` … `phase-6`, `backend`, `frontend`, `infra`, `docs`, `human-step`.
