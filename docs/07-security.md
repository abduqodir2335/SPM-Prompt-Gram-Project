# 07 — Security

This page lists the security rules of the product, of the pipeline and of the server account. It also lists the limits that we accept in this course project.

## 1. Application rules

### Passwords and sessions
- Hash passwords with Werkzeug `generate_password_hash` (scrypt). Never log, return or store a plain password.
- Login errors are generic. Registration may say "username taken" (accepted for usability).
- Session cookie: `HttpOnly`, `SameSite=Lax`, path `/`, lifetime 7 days, name `pg_session_<WEB_PORT>`. `Secure` is `false` on the course server because there is no HTTPS (limit L-1).
- Regenerate the session at login (clear it first, then log the user in).
- Rate limits (Flask-Limiter, in-memory): login 10/min and register 5/min per address, comments 30/min per user. Answer `429`.

### CSRF
- All students' apps share the host name `spm.iotserver.uz`. Browsers send cookies to every port of a host, and treat all ports as the same site. `SameSite` therefore does **not** protect one student's app from a page served by another port.
- Protection: Flask-WTF `CSRFProtect` on every state-changing request, token in the `X-CSRFToken` header. No exception lists.
- The unique cookie name per port stops sessions of different apps from overwriting each other.

### Input and output
- Validate every request body, query and path value on the server with Pydantic. Enforce the same limits in the database.
- Use SQLAlchemy queries with bound parameters. Never build SQL with string formatting.
- React escapes text by default. Never use `dangerouslySetInnerHTML`. User text is plain text; no Markdown or HTML rendering in v1.0.
- User-provided links are not rendered as clickable links in v1.0.

### Authorisation
- Check ownership on the server for every edit and delete (post, attachment, comment). The UI hiding a button is not a control.
- Return `404` for a missing resource and `403` for someone else's resource.
- Never trust an ID or `author_id` from the client. The author is always the session user.

### File uploads
- Allow-list only: PNG, JPEG, WebP, GIF, PDF, TXT, MD. SVG and HTML are **not** allowed (they can carry scripts).
- Decide the type from the **content**:
  - PNG, JPEG, GIF, WebP, PDF: check the file signature (magic bytes).
  - TXT, MD: the bytes must decode as UTF-8 and must not contain a NUL byte.
  - The extension must match the detected type.
- Limits: 5 MB per file (`MAX_CONTENT_LENGTH` in Flask and `client_max_body_size` in nginx), 4 files per post.
- Store under a random server-generated name. Never use the client's file name as a path. Keep the original name only in the database, and clean it for the `Content-Disposition` header.
- Serve through the API only, with `X-Content-Type-Options: nosniff`. Images `inline`; everything else `attachment`.
- The upload folder is a volume without execute use. The API never runs or parses uploaded files beyond the signature check.

### HTTP headers (set by nginx on every response)
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: same-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Content-Security-Policy: default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'
```
No `Strict-Transport-Security` while the app is HTTP only.

nginx trap: a `location` with its own `add_header` drops the headers of the `server` block unless `add_header_inherit merge;` is set (02 section 2). Check the headers on `/`, on an `/assets/` file and on an `/api/` response.

### Errors and logs
- `500` answers have no stack trace. Flask debug mode is off outside development.
- Logs are JSON lines on stdout: time, level, request ID, method, path, status, duration, user ID. Never log passwords, cookies, CSRF tokens, `Authorization` headers or file contents.

## 2. Container rules

- `api` and `web` run as non-root users, with `read_only: true`, `cap_drop: ALL`, `no-new-privileges`.
- Only `web` publishes a port. `db` and `api` have no published port.
- Base images are official images, pinned by digest in Dockerfiles and compose. Dependabot updates the digests.
- Multi-stage builds: the final images contain no compilers, no `node_modules`, no tests, no `.git`.
- `.dockerignore` excludes `.env*`, `.git`, tests, caches.
- Memory, CPU and log limits as in 02.

## 3. Pipeline and repository rules

- Secrets live only in GitHub environment `production` and in `~/promptgram/.env` on the server. Nowhere else.
- `deploy/.env.example` is a template with placeholders (`CHANGE_ME`). It is the only `.env` file of the server in the repository. Each student creates the real file on the server with their own random values (`openssl rand -hex …`). Do not reuse a password from another service. Do not copy another student's values.
- The deployment SSH key is **dedicated**: used only by GitHub Actions, no passphrase, stored as an environment secret, restricted on the server with the `restrict` option in `authorized_keys` (no port, agent or X11 forwarding, no terminal).
- The server host key is pinned (`DEPLOY_KNOWN_HOSTS`). Host key checking is never disabled.
- The registry token on the server is the job's short-lived `GITHUB_TOKEN`, passed on stdin, logged out after the pull.
- Workflows use least-privilege `permissions`. No `pull_request_target`. Only GitHub-owned actions, pinned to commit SHAs. The repository setting *Allow actions created by GitHub* blocks every other action. No secret is ever given to an action: registry login and SSH are plain shell.
- `main` is protected by a ruleset: pull request required, status checks required, no force push, no deletion.
- Dependabot alerts, security updates and version updates are on (free). Secret scanning with push protection and CodeQL are on when the organisation licence allows (05 section 9).
- `.gitignore` blocks `.env` files and key files. Review every diff for secrets before you merge; without push protection, you are the secret scanner.

If a secret leaks (committed, pasted in a chat, printed in a log): treat it as public. **Rotate it first**, then clean up. For the deploy key: remove the public key line from `authorized_keys`, create a new pair, update the secret.

## 4. Rules for work with AI agents

- Never paste a real secret, key or `.env` content into an AI chat or prompt.
- Do not let the agent run commands on the server that change state. The pipeline deploys.
- Check every dependency that an agent proposes: does the package exist under exactly that name, is it the well-known one? AI tools sometimes invent package names, and attackers register those names.
- Read the diff of workflow files and Dockerfiles with extra care. These files run with access to secrets.
- Text from outside (web pages, issue comments, file contents) can contain instructions aimed at the agent. The agent follows only you and `AGENTS.md`.

## 5. Known limits (accepted for this course)

| ID | Limit | Risk | What we do now | Real fix |
|---|---|---|---|---|
| L-1 | **No HTTPS.** The app is served on plain HTTP. | Passwords and session cookies can be read on the network path. | Use **test passwords only**, never a password you use elsewhere. The register page shows this warning. `SESSION_COOKIE_SECURE` is a switch, ready for HTTPS. | The teacher adds a TLS reverse proxy with a domain per student. |
| L-2 | All student apps share one host name. | Cookies ignore ports. When a user opens another student's app, the browser also sends it the session cookie of your app. A hostile app could capture that cookie. | Unique cookie name; CSRF tokens; test accounts only. | One sub-domain per student. |
| L-3 | Sessions are signed cookies without a server-side store. | A stolen cookie works until it expires (7 days). No "log out everywhere". | Short lifetime; rotate `SECRET_KEY` on the server to end all sessions. | Server-side session table. |
| L-4 | Rate limits are counted in the memory of the one gunicorn worker. | Counters reset when the container restarts. If someone raises the worker count, each worker counts on its own. | Accepted. Keep one worker (02 section 2). | Shared store (Redis). |
| L-5 | No email verification and no password reset. | Fake emails; a forgotten password means a new account. | Accepted. Out of scope. | Mail service. |
| L-6 | Backups stay on the same server. | Server loss means data loss. | Download a manual backup before the demo. | Off-site backup. |
| L-7 | No moderation. | Unwanted content stays until the author deletes it. | Class-only users. | Admin role (stretch). |
| L-8 | The deploy key lets GitHub Actions run any command as your server user. | A leaked key or a malicious workflow change gives access to your server account (not to other students, not to root). | Environment secret limited to `main`; ruleset on `main`; review workflow changes; rotate on doubt. | A forced-command key that can only run the deploy script. |

## 6. Security review checklist (Phase 6)

- [ ] Every state-changing endpoint: login required, CSRF required, ownership checked, tests exist.
- [ ] No endpoint returns `password_hash` or another user's email.
- [ ] Upload tests: wrong signature, wrong extension, oversize, fifth file, path characters in the file name.
- [ ] No secret in the repository or its history: secret scanning shows no alert (when enabled), and a manual search finds nothing: `git log -p | grep -inE 'password|secret|token|BEGIN .* PRIVATE KEY'`.
- [ ] CodeQL shows no open alert of high or critical severity (when enabled).
- [ ] Every action in `.github/workflows/` is GitHub-owned and pinned to a commit SHA.
- [ ] Response headers present on `/`, `/api/health` and a media response.
- [ ] `docker compose ps` on the server: only `web` has a published port.
- [ ] Containers run as non-root (`docker compose exec api id`).
- [ ] Server `.env`: mode `600`, no `CHANGE_ME`, `SECRET_KEY` at least 32 characters. The repository has only `deploy/.env.example` with placeholders.
- [ ] Dependabot alerts: none open with a fix available.
- [ ] An independent AI review of the whole code base with the prompt "Security review" in `docs/prompts.md` (Part B), using a different tool or a fresh session than the one that wrote the code.
