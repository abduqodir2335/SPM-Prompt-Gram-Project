# 06 — Testing

## 1. Rule number one: tests never touch real data

There are four separate data environments. They share nothing.

| Environment | Runs where | Compose project | Database | Uploads | Lifetime |
|---|---|---|---|---|---|
| Production | SPM server | `promptgram` | `promptgram` in volume `promptgram_pgdata` | volume `promptgram_uploads` | Permanent |
| Development | Your computer | `promptgram-dev` | `promptgram` in a local dev volume | local dev volume | Until you delete it |
| Unit / integration tests | Your computer, GitHub Actions | dev stack, or CI service container | **`promptgram_test`** | a temporary folder per test run | Emptied by every run |
| End-to-end tests | GitHub Actions, or your computer | `promptgram-e2e` | temporary (`tmpfs`) | temporary | Deleted with `down -v` after the run |

Safety mechanisms (all required):

1. **Guard in `backend/tests/conftest.py`.** Before any test runs, the setup checks `APP_ENV == "test"` **and** that the database name in `DATABASE_URL` ends with `_test`. If not, it stops the whole run with a clear message. This guard has its own unit test.
2. **Different database, not only different tables.** The dev PostgreSQL container creates `promptgram_test` next to `promptgram` with an init script.
3. **Production credentials exist only on the server.** The student types them into `~/promptgram/.env` there, and they never leave it. No developer machine and no CI job can connect to the production database: the `db` container has no published port.
4. **The post-deployment check is read-only.** It calls `GET /api/health` and `GET /`. It creates no user, no post, nothing.
5. **Demo data.** `flask seed-demo` refuses to run when `APP_ENV=production`.

## 2. Test levels

| Level | Tool | What it covers | Where it runs |
|---|---|---|---|
| Backend unit | pytest | Services, validation, cursor encoding, file type detection, password hashing | Local, CI `backend` |
| Backend integration | pytest + Flask test client + real PostgreSQL | Every endpoint: success, 401, 403, 404, 422, paging, ownership, CSRF, idempotent like | Local, CI `backend` |
| Migration | Alembic commands | upgrade → downgrade → upgrade on an empty database; models match migrations | CI `backend` |
| Frontend unit / component | Vitest + Testing Library + MSW (mock API) | Forms and their errors, post card, like button optimistic update, copy button, route guard | Local, CI `frontend` |
| Static | Ruff, ESLint, TypeScript `strict` | Style, obvious bugs, types | Local, CI |
| End-to-end | Playwright (Chromium) against the **built images** | The main user journeys through nginx, API and database | CI `image`, local `make e2e` |
| Accessibility | `@axe-core/playwright` inside the e2e run | No serious or critical violations on login, feed, post detail, post form | CI `image` |
| Security checks | Dependabot alerts and updates; CodeQL and secret scanning when enabled (05 section 9) | Known vulnerabilities in dependencies, base images and actions; security bugs; committed secrets | GitHub, on every push (Security tab) |
| Post-deploy smoke | `curl` in `deploy.yml` | Health, version, home page | After every deployment |

SQLite is **not** used for tests. Tests run on PostgreSQL 18, the same engine as production.

## 3. Backend test rules

- Each test is independent. A fixture gives every test a clean state (transaction rolled back after the test, or tables truncated).
- Use factory helpers (`make_user()`, `make_post(author=...)`) instead of hand-written setup in every test.
- Each endpoint has at least: one success test, one "not logged in" test, one validation test, and one "not the owner" test where ownership applies.
- Uploads in tests use tiny in-memory files and a temporary `UPLOAD_DIR` (`tmp_path`).
- No network calls. No sleeps. Time-dependent code takes a clock that tests can set.
- Coverage: line coverage of `backend/app` ≥ **80 %**. The limit is set in `pyproject.toml`.

## 4. Frontend test rules

- Test behaviour that a user sees: text, roles, labels. Do not test implementation details or CSS classes.
- Mock the API at the network level with MSW. Do not mock the app's own modules.
- Each form: valid submit, each validation error, server error.
- Coverage: line coverage of `frontend/src` ≥ **70 %** (pages and components).

## 5. End-to-end scenarios

The suite grows with the phases. Each run starts on an empty database and creates its own users with random names.

| Phase | Scenario |
|---|---|
| 1 | The home page loads. `/api/health` returns `ok` with the expected version. |
| 2 | Register → see the feed → log out → log in again → reload stays logged in. Wrong password shows the generic error. Protected route redirects to login. |
| 3 | Create a post → it is first in the feed → open it → copy the prompt → edit it → delete it. A second user cannot see Edit/Delete on it. Profile page lists the user's posts. |
| 4 | Create a post with one PNG and one text file → image shows, file link downloads. A too-large file and a wrong type show an error. |
| 5 | Second user likes and comments on the first user's post → counts change → unlike → delete own comment. |
| 6 | Mobile viewport (360 px) smoke test of the full journey. Accessibility checks on four pages. |

Keep the suite short (target: under 3 minutes). Detailed cases belong in backend and component tests.

## 6. What runs when

| Moment | Checks |
|---|---|
| While coding (you or the agent) | The tests of the changed area |
| Before opening a PR | `make check` (all lint + unit + integration). `make e2e` when a user journey changed. |
| On every PR and on `main` | Full `ci.yml`: backend, frontend, image (build + e2e). GitHub's security checks run beside it. |
| After every deployment | Post-deploy smoke |
| Phase 6 | Manual exploratory test on a phone and a second browser; backup restore drill; feed timing check with 1000 seeded posts **in the dev stack**, never in production |

## 7. Test-first workflow with an AI agent

1. Give the agent the story ID and its acceptance criteria.
2. The agent writes the tests first. Each acceptance criterion maps to at least one test. The test name contains the ID, for example `test_fr06_ac3_invalid_title_is_rejected`.
3. Run the tests. They must **fail** for the right reason.
4. The agent writes the code until the tests pass.
5. You read the tests before you read the code. Wrong tests are worse than wrong code: they make wrong code look right.

Never accept a change where the agent edited a failing test to make it pass, unless the test was wrong and the PR says why.
