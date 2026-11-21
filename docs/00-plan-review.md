# 00 — Review of the first rough plan

This page records what the first plan said, what was wrong or missing, and what replaced it. The corrected requirements are in [01-requirements.md](01-requirements.md).

## 1. The first plan

> **PromptGram** — similar to Instagram but for AI prompts.
> User stories: auth page; each user has an explore page (scroll other users' posts); user can like or comment on each post; user can create a new post about his prompt and attach images (or any files).
> Milestones: working auth page.
> Stack: Python Flask, PostgreSQL, React.

## 2. Findings

| # | Finding | Why it matters | Correction |
|---|---|---|---|
| 1 | "Auth page" is a screen, not a user story. | A story must say who wants what and why, so that it can be tested. | Three stories: register, log in, log out (FR-01 to FR-03), each with acceptance criteria. |
| 2 | The product's main value is missing: **using** a prompt. | People come to copy a prompt, not only to look at it. | A post has a dedicated `prompt` field and a **Copy prompt** button (FR-07). |
| 3 | A "post" is not defined. | The agent would invent fields. Every student would build a different thing. | Post = title, prompt text, optional description, optional model name, 0–4 attachments (data model in 03). |
| 4 | "Attach images (or any files)" is unsafe. | An uploaded HTML or SVG file can run scripts in other users' browsers. Unlimited size fills the 3 GB disk quota. | Allow-list of types, 5 MB per file, 4 files per post, safe download headers (FR-09, security rules in 07). |
| 5 | "Explore page" has no rules. | Loading every post at once does not scale and is slow. | Newest first, 20 per page, cursor pagination, "load more" on scroll (FR-05). |
| 6 | No ownership rules. | Without them anyone could edit or delete any post. | Only the author edits or deletes a post or comment (FR-08, FR-12). The API returns 403 otherwise. |
| 7 | "Like" has no rules. | Double likes, likes on own post, counts. | One like per user per post, toggle, idempotent API, count shown (FR-10). |
| 8 | No profile page. | Users need to find "my posts" and another user's posts. | Simple profile page (FR-13). |
| 9 | Only one milestone ("working auth page"). | No ordering, no way to see progress, deployment comes last and fails late. | Seven phases. Phase 1 deploys a walking skeleton **before** any feature (09-plan). |
| 10 | No non-functional requirements. | Security, data safety, performance and deployment were left to chance. | NFR list in 01: security, persistence, test isolation, resource limits, accessibility. |
| 11 | No deployment or operations requirements. | The course goal is a professional CI/CD pipeline. | Containers only on the server, images from GHCR, automatic deploy with health gate, rollback, backups (05). |
| 12 | No test strategy, no rule for test data. | Tests could write into the real database. | Three separate data environments and a hard guard in the test setup (06). |
| 13 | Versions and supporting tools not chosen. | "Flask + React + Postgres" leaves 20 more choices open. Each choice is a question to the teacher. | Every choice is fixed and explained (README section 3, 10-decisions). |
| 14 | No scope limit. | AI agents add features nobody asked for. | Explicit "not in v1.0" list and a stretch backlog (01 section 5). |
| 15 | No rules for AI agents. | Three tools, three behaviours, duplicated instruction files. | One `AGENTS.md`; thin pointers for Claude Code and Copilot; shared workflow (08). |
| 16 | The server environment was not considered. | The server has hard limits that shape the design. | See section 3. |

## 3. Facts about the SPM server that shape the design

Checked on 2026-11-14.

| Fact | Effect on the design |
|---|---|
| Each student has **rootless Docker** (own daemon, no sudo). | Containers run as the student. Ports below 1024 are not possible. No system services. |
| Disk quota **3 GB soft / 4 GB hard** per student. Docker images count. | Small images (slim/alpine bases, multi-stage builds). The deploy script prunes old images. No builds and no tests on the server. Upload limits. Log rotation. |
| The server has **2 CPUs and 7.7 GB RAM** for all students. | Memory and CPU limits per container. CI runs on GitHub-hosted runners, not on the server. |
| Each student has **50 public ports** (for example 11000–11049). No domain per student, **no HTTPS**. | The app is served on plain HTTP at `http://spm.iotserver.uz:<first port>`. Cookies cannot use the `Secure` flag. Use test passwords only (07, limit L-1). |
| All students share **one host name**. Browsers share cookies between ports of one host. | Each deployment uses its own cookie name. CSRF protection is required, not optional (07). |
| SSH (port 22) is open to the internet. Password and key login work. | GitHub-hosted runners can deploy over SSH with a dedicated key. |
| The org has **deploy keys disabled**. | Not needed: the server never clones the repository. |

## 4. What stayed the same

- The idea: Instagram-like sharing of AI prompts.
- The stack from the brief: React, Flask, PostgreSQL.
- The four feature areas: authentication, explore feed, likes and comments, posts with attachments.
