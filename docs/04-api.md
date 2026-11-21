# 04 — API contract

Base path: `/api`. Versioned resources: `/api/v1`. Format: JSON, UTF-8, `snake_case` keys.
This contract is binding for backend and frontend. Change this file first, then the code.

## 1. General rules

### Authentication
- Session cookie, set by login or register. `HttpOnly`, `SameSite=Lax`, name from `SESSION_COOKIE_NAME`, lifetime 7 days.
- Every endpoint needs a logged-in member, **except**: `GET /api/health`, `GET /api/v1/auth/csrf`, `POST /api/v1/auth/register`, `POST /api/v1/auth/login`.
- Without a valid session the API answers `401 unauthorized`. It never redirects.

### CSRF
- Every `POST`, `PUT`, `PATCH`, `DELETE` request must send the header `X-CSRFToken: <token>`.
- The client gets the token from `GET /api/v1/auth/csrf`. The frontend API client fetches it once, keeps it in memory, and fetches a new one after login, logout, or a `403 csrf_failed` answer (one retry).

### Errors
One format for every error:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Some fields are not valid.",
    "fields": { "title": "Must be 3 to 120 characters." }
  }
}
```

`fields` is present only for `validation_error`.

| Status | `code` | When |
|---|---|---|
| 400 | `bad_request` | Body is not valid JSON or multipart, bad cursor |
| 401 | `unauthorized` | Not logged in; wrong login credentials (`invalid_credentials`) |
| 403 | `forbidden` | Logged in but not the owner |
| 403 | `csrf_failed` | Missing or wrong CSRF token |
| 404 | `not_found` | Resource does not exist |
| 409 | `conflict` | Username or email already used (also reported in `fields`); attachment limit reached (`attachment_limit`) |
| 413 | `file_too_large` | File over 5 MB |
| 415 | `unsupported_file_type` | File type not on the allow-list |
| 422 | `validation_error` | Field validation failed |
| 429 | `rate_limited` | Too many requests |
| 500 | `internal_error` | Unexpected error. No stack trace or internal detail in the body. |

### Pagination
- Query parameters: `limit` (default 20, maximum 50) and `cursor` (opaque string).
- Response: `{ "items": [...], "next_cursor": "..." }`. `next_cursor` is `null` on the last page.
- The cursor encodes the sort key of the last item (`created_at`, `id`) as URL-safe base64. Clients must not build or read it.

### Objects

**User**
```json
{ "id": 7, "username": "aziz", "created_at": "2026-11-14T08:30:00Z" }
```
The current user's own object (`/auth/me`, login, register) also has `"email"`.

**Attachment**
```json
{
  "id": 31, "kind": "image", "original_name": "result.png",
  "content_type": "image/png", "size_bytes": 482113,
  "url": "/api/v1/media/31"
}
```

**Post**
```json
{
  "id": 12,
  "author": { "id": 7, "username": "aziz" },
  "title": "Explain code like a senior reviewer",
  "prompt": "You are a senior engineer. Review the code below...",
  "description": "Works best with the full file.",
  "model": "Claude",
  "attachments": [],
  "like_count": 3,
  "comment_count": 1,
  "liked_by_me": false,
  "edited": false,
  "created_at": "2026-11-14T08:31:00Z",
  "updated_at": "2026-11-14T08:31:00Z"
}
```
In list responses `prompt` is complete (the client cuts it to 300 characters for the card).

**Comment**
```json
{ "id": 5, "post_id": 12, "author": { "id": 9, "username": "bek" }, "body": "Nice one", "created_at": "2026-11-14T09:00:00Z" }
```

## 2. Endpoints

### Health (Phase 1)

| Method | Path | Auth | Result |
|---|---|---|---|
| GET | `/api/health` | no | `200 {"status":"ok","version":"<commit sha>","db":"ok"}`. `503 {"status":"degraded","version":"…","db":"error"}` when the database does not answer `SELECT 1`. |

The pipeline compares `version` with the deployed commit.

### Auth (Phase 2)

| Method | Path | Body | Result |
|---|---|---|---|
| GET | `/api/v1/auth/csrf` | — | `200 {"csrf_token":"…"}` |
| POST | `/api/v1/auth/register` | `{"username","email","password"}` | `201` User (with email). Logs the user in. `409`/`422` on errors. Rate limit: 5 per minute per address. |
| POST | `/api/v1/auth/login` | `{"identifier","password"}` — identifier is username or email | `200` User (with email). `401 invalid_credentials`. Rate limit: 10 per minute per address. |
| POST | `/api/v1/auth/logout` | — | `204`. Clears the session. |
| GET | `/api/v1/auth/me` | — | `200` User (with email) or `401`. |

### Posts (Phase 3)

| Method | Path | Body / query | Result |
|---|---|---|---|
| GET | `/api/v1/posts` | `?limit&cursor&author=<username>` | `200` page of Post, newest first. Unknown `author` → `404`. |
| POST | `/api/v1/posts` | `{"title","prompt","description"?,"model"?}` | `201` Post |
| GET | `/api/v1/posts/{id}` | — | `200` Post / `404` |
| PATCH | `/api/v1/posts/{id}` | any of `title`, `prompt`, `description`, `model` | `200` Post. `403` if not the author. Sets `updated_at`. |
| DELETE | `/api/v1/posts/{id}` | — | `204`. `403` if not the author. Deletes attachments (rows and files), likes, comments. |

Text rules: trim leading and trailing white space on `title`, `model`, `description`. Keep `prompt` exactly, except trailing white space. An empty string for an optional field means `null`.

### Users (Phase 3)

| Method | Path | Result |
|---|---|---|
| GET | `/api/v1/users/{username}` | `200 {"id","username","created_at","post_count"}` / `404` |

A user's posts come from `GET /api/v1/posts?author=<username>`.

### Attachments (Phase 4)

| Method | Path | Body | Result |
|---|---|---|---|
| POST | `/api/v1/posts/{id}/attachments` | `multipart/form-data`, one part named `file` | `201` Attachment. `403` if not the author. `409 attachment_limit` when the post has 4. `413`, `415` per the rules. |
| DELETE | `/api/v1/attachments/{id}` | — | `204`. `403` if not the author of the post. |
| GET | `/api/v1/media/{id}` | — | `200` file bytes. Needs login. Headers: `Content-Type` from the database, `X-Content-Type-Options: nosniff`, `Cache-Control: private, max-age=86400`, and `Content-Disposition: inline` for images, `attachment; filename="…"` for other files. |

The client creates the post first (JSON), then uploads the files one by one. If an upload fails, the post still exists and the UI shows which file failed.

Allowed files (the server decides the type from the content, see 07):

| Type | Extensions | `content_type` | `kind` |
|---|---|---|---|
| PNG | `.png` | `image/png` | image |
| JPEG | `.jpg`, `.jpeg` | `image/jpeg` | image |
| WebP | `.webp` | `image/webp` | image |
| GIF | `.gif` | `image/gif` | image |
| PDF | `.pdf` | `application/pdf` | file |
| Text | `.txt` | `text/plain; charset=utf-8` | file |
| Markdown | `.md` | `text/markdown; charset=utf-8` | file |

### Likes (Phase 5)

| Method | Path | Result |
|---|---|---|
| PUT | `/api/v1/posts/{id}/like` | `200 {"liked":true,"like_count":4}`. Repeating it gives the same answer. |
| DELETE | `/api/v1/posts/{id}/like` | `200 {"liked":false,"like_count":3}`. Repeating it gives the same answer. |

### Comments (Phase 5)

| Method | Path | Body / query | Result |
|---|---|---|---|
| GET | `/api/v1/posts/{id}/comments` | `?limit&cursor` | `200` page of Comment, **oldest first** |
| POST | `/api/v1/posts/{id}/comments` | `{"body"}` | `201` Comment. Rate limit: 30 per minute per user. |
| DELETE | `/api/v1/comments/{id}` | — | `204`. `403` if not the comment author. |

## 3. Cross-cutting behaviour

- Unknown JSON fields in a request are ignored. Wrong types are a `422`.
- `Content-Type` of JSON requests must be `application/json`, otherwise `400`.
- IDs in paths are positive integers. Anything else is a `404`.
- Every response has `X-Request-ID` (generated when the client did not send one). The same ID is in the log line.
- Unknown paths under `/api/` return the JSON `404`, never the React `index.html`.
- Rate limits use the client address from `X-Forwarded-For` set by the `web` container (the API trusts exactly one proxy hop).
