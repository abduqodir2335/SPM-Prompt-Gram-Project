# 01 — Requirements

Product: **PromptGram**, a web app to share AI prompts.
Release described here: **v1.0** (end of Phase 6).

Words used in this document: **must** = required for v1.0. **should** = do it if time allows inside the phase. **stretch** = only after v1.0.

## 1. Users

| Role | Description |
|---|---|
| Visitor | Not logged in. Sees only the login and register pages. |
| Member | Logged in. Can do everything in section 3. |

There is no admin role in v1.0.

## 2. Glossary

| Term | Meaning |
|---|---|
| Post | One shared prompt: title, prompt text, optional description, optional model name, 0–4 attachments. |
| Prompt | The text that a user would paste into an AI tool. The main field of a post. |
| Attachment | A file added to a post: an example result image, a PDF or a text file. |
| Feed / Explore | The list of all posts, newest first. |
| Author | The member who created a post or comment. |

## 3. Functional requirements (user stories)

Each story has an ID, a phase and acceptance criteria (AC). An AC is a test: it must be automated.

### Authentication (Phase 2)

**FR-01 Register** — As a visitor, I want to create an account so that I can post and react.
- AC1: The form asks for username, email and password. A valid form creates the account, logs me in and opens the feed.
- AC2: Username: 3–30 characters, `a–z`, `0–9`, `_`. Stored in lower case. Must be unique.
- AC3: Email: valid format, stored in lower case, must be unique. No confirmation email is sent.
- AC4: Password: 8–128 characters. Stored only as a hash.
- AC5: A taken username or email shows an error on that field. Nothing is created.
- AC6: Each invalid field shows its own error message. The form keeps the typed values (except the password).

**FR-02 Log in** — As a visitor with an account, I want to log in so that I can use the app.
- AC1: I log in with username **or** email, and password.
- AC2: Wrong credentials show one generic message ("Invalid username or password"). The message does not say which part was wrong.
- AC3: After login, a page reload keeps me logged in. The session lasts 7 days.
- AC4: After 10 failed attempts per minute from one address, the API answers 429.
- AC5: If I open a protected page while logged out, I see the login page. After login I return to the page I wanted.

**FR-03 Log out** — As a member, I want to log out so that nobody else uses my account on this device.
- AC1: "Log out" ends the session and opens the login page.
- AC2: After logout, the browser's Back button does not show protected data (the API answers 401).

**FR-04 Current user** — As a member, I see my username in the header on every page, with links to my profile and to log out.

### Posts and feed (Phase 3)

**FR-05 Explore feed** — As a member, I want to scroll all posts so that I can discover prompts.
- AC1: The home page `/` shows posts from all users, newest first.
- AC2: The page loads 20 posts. More posts load when I reach the end (infinite scroll with a visible "Load more" button as fallback).
- AC3: Each card shows: author username (link to profile), relative time, title, the first 300 characters of the prompt, model name if set, first image attachment if any, like count, comment count.
- AC4: An empty feed shows "No posts yet" and a button to create the first post.
- AC5: Loading and error states are visible. A failed load offers "Try again".

**FR-06 Create a post** — As a member, I want to publish a prompt so that others can use it.
- AC1: Fields: title (required, 3–120 characters), prompt (required, 10–8000 characters), description (optional, up to 2000), model (optional, up to 60, free text such as "Claude" or "GPT").
- AC2: A valid form creates the post and opens its detail page. The post is at the top of the feed.
- AC3: Invalid fields show their own messages. Nothing is created.
- AC4: The prompt keeps its line breaks and spaces when shown.

**FR-07 View and copy a post** — As a member, I want to open a post and copy its prompt so that I can use it.
- AC1: The detail page `/posts/:id` shows all fields, attachments, like button with count, and comments.
- AC2: The prompt is shown in a monospace block. A **Copy prompt** button copies the exact prompt text to the clipboard and confirms with "Copied".
- AC3: An unknown post ID shows a "Post not found" page (API 404).

**FR-08 Edit and delete my post** — As an author, I want to fix or remove my post.
- AC1: Edit and Delete are visible only on my own posts.
- AC2: Edit changes title, prompt, description and model with the same validation as FR-06. The post shows "edited".
- AC3: Delete asks for confirmation. It removes the post, its attachments (files too), likes and comments.
- AC4: The API answers 403 when another member tries to edit or delete my post.

**FR-13 Profile** — As a member, I want to see one user's posts.
- AC1: `/u/:username` shows the username, join date, number of posts, and that user's posts, newest first, with the same cards and paging as the feed.
- AC2: An unknown username shows "User not found" (API 404).

### Attachments (Phase 4)

**FR-09 Attach files** — As an author, I want to add example results to my post.
- AC1: I can add up to **4** files when I create or edit a post. I can remove a file from my own post.
- AC2: Allowed types: PNG, JPEG, WebP, GIF, PDF, plain text (`.txt`), Markdown (`.md`). Maximum **5 MB** per file.
- AC3: A file of another type or size is rejected with a clear message (API 415 or 413). The post itself is not lost.
- AC4: Images show inside the post (detail page: all images; feed card: first image). Other files show as a download link with name and size.
- AC5: Files are available only to logged-in members.
- AC6: The server checks the real content of the file, not only its name (see 07-security).

### Likes and comments (Phase 5)

**FR-10 Like** — As a member, I want to like a post so that good prompts get noticed.
- AC1: The like button toggles. The count changes at once (optimistic update) and is corrected if the request fails.
- AC2: One member can like one post once. Repeating the same request does not change the count (idempotent).
- AC3: I can like my own post.
- AC4: The feed and detail page show the count and whether I liked the post.

**FR-11 Comment** — As a member, I want to comment on a post so that I can give feedback.
- AC1: A comment is 1–1000 characters of plain text.
- AC2: Comments show under the post, oldest first, with author and relative time. 20 load at first; "Load more" loads the next 20.
- AC3: A new comment appears without a page reload. The comment count updates.

**FR-12 Delete my comment** — As a comment author, I can delete my comment after a confirmation. The API answers 403 for another member's comment.

## 4. Non-functional requirements

| ID | Requirement | How it is checked |
|---|---|---|
| NFR-01 Security | Passwords hashed with scrypt. Session cookie `HttpOnly`, `SameSite=Lax`. CSRF token on every state-changing request. All input validated on the server. Ownership enforced on the server. Rules in 07-security. | Tests for 401/403/422; security review in Phase 6. |
| NFR-02 Data persistence | Users, posts, comments, likes and files survive a redeploy, a container restart and a server reboot. | Phase 1 and Phase 6 exit checks. |
| NFR-03 Test isolation | No automated test reads or writes production data. | Guard in test setup; pipeline design (06). |
| NFR-04 Deployment | Every merge to `main` that passes all checks is deployed automatically. A failed deployment does not leave the app down: the script returns to the previous release. | Pipeline (05). |
| NFR-05 Server footprint | Only containers on the server, no source code. All images together under **1 GB**. Memory limits: api 256 MB, db 256 MB, web 64 MB. Container logs rotated (3 × 10 MB). | `docker system df`, compose file. |
| NFR-06 Performance | With 1000 posts, the feed API answers in under 300 ms on the server (p95). Lists never return more than 50 items. | Seed script + timing check in Phase 6. |
| NFR-07 Reliability | Containers restart automatically (`restart: unless-stopped`). Each has a health check. | Compose file; reboot is covered by user lingering on the server. |
| NFR-08 Accessibility | Keyboard use for all actions. Labels on all form fields. Visible focus. Colour contrast AA. | Playwright + axe check on main pages. |
| NFR-09 Responsive | Usable from 360 px width to desktop. | Manual check on a phone; Playwright mobile viewport smoke test. |
| NFR-10 Browser support | Current Chrome, Edge, Firefox, Safari. | e2e runs on Chromium; manual check on one other browser. |
| NFR-11 Observability | `GET /api/health` reports status, version (commit SHA) and database state. The API logs one JSON line per request to stdout, without secrets or passwords. | Health test; log review. |
| NFR-12 Maintainability | Lint and format checks pass. Backend line coverage ≥ 80 %. Frontend line coverage ≥ 70 %. | CI gates. |
| NFR-13 Configuration | All settings come from environment variables. One image runs in every environment. | Architecture (02). |

## 5. Scope

### In v1.0
Everything in sections 3 and 4.

### Not in v1.0 (do not build without a decision record)
- Email sending: confirmation, password reset.
- Admin role and moderation.
- Follow users, personal feed, notifications.
- Tags, search, sorting by popularity.
- Editing comments, nested replies.
- Avatars, profile editing.
- Image resizing or thumbnails.
- Real-time updates (WebSocket).
- HTTPS (needs a change on the server by the teacher).
- OAuth / social login.

### Stretch backlog (after v1.0, in this order)
1. Tags on posts and filter by tag.
2. Text search over title and prompt.
3. Sort the feed by "most liked this week".
4. Profile editing with display name and bio.
5. Dark mode.

## 6. Assumptions and constraints

- One student builds and deploys one instance. Each instance has few users (class size) and little data.
- The app runs on plain HTTP on the course server. Users must not use real passwords (limit L-1 in 07).
- The disk quota is 3 GB per student for images, volumes, logs and backups together.
- The stack is fixed by the course: React, Flask, PostgreSQL.
