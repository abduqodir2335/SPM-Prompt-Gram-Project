# Teacher guide

Notes for the person who runs the course. Students do not need this page.

## 1. Give the template to students

The template is private. A student can use it only with read access to it.

**Option A — "Use this template" (simple)**
1. Give the student team read access to the template repository:
   `gh api -X PUT orgs/ttpu-spm/teams/<team-slug>/repos/ttpu-spm/SPM-PromptGram-Test -f permission=pull`
2. Students follow STUDENT-GUIDE step 0.2. They become **admin** of the repository they create (they need admin for environments, secrets and rulesets).
3. Requirement: organisation members may create private repositories (this is on today).

**Option B — GitHub Classroom**
1. Create an individual assignment with this repository as the starter (template) repository. Visibility private.
2. Turn on **"Grant students admin access to their repository"**. Without admin, students cannot create the `production` environment, its secret, or the ruleset.

In both cases, check one student repository: the student sees the **Settings** tab.

## 2. Organisation settings to check

| Setting | Needed value | Why |
|---|---|---|
| Actions → General → Policies | Actions allowed for private repositories. The project needs **only actions created by GitHub** (`actions/*`, `github/*`). You can enforce this for the whole organisation: *Allow ttpu-spm, and select non-ttpu-spm, actions* → *Allow actions created by GitHub*. Students set the same policy in their repository. | Course rule: GitHub tools only, no third-party actions (decision D-21). |
| Actions → Workflow permissions | Read (default) is enough. | Workflows request `packages: write` themselves. |
| Packages | Members may publish **private** container packages. | Images go to GHCR. |
| Rulesets on private repositories | Available on the current plan. | Branch protection for `main`. |
| Secret Protection and Code Security (former Advanced Security) | **Your decision.** On private repositories, secret scanning, push protection, CodeQL and dependency review need these products. They are billed per active committer unless your plan includes them. Dependabot is free and always on. | Tell the class "on" or "off" before Phase 0. The documents work in both cases (05 section 9). |
| Projects | Members may create organisation projects. | Each student keeps a board for the backlog. |
| Actions minutes | A full pipeline run takes about 6–10 minutes. Estimate: 13 students × 60 runs ≈ 130 hours for the whole project. | Check the plan's included minutes. |

Deploy keys can stay disabled in the organisation. The server never clones a repository.

## 3. Server facts (checked 2026-11-14)

| Item | Value |
|---|---|
| Role | Shared course **test server**. One account, home folder, rootless Docker daemon and port range per student. Students deploy and run in parallel. |
| Host | `spm.iotserver.uz` (Azure), Ubuntu 24.04, 2 vCPU, 7.7 GB RAM |
| Disk | 29 GB root, **9.8 GB free** |
| Docker | Rootless per student, Docker 29.9, Compose v5.6, buildx; context `rootless`; lingering on; cgroup v2 with `cpu memory pids` delegated (limits work) |
| Quota | 3 GB soft / 4 GB hard per student (home, includes Docker data) |
| Ports | 50 per student, open to the internet |
| SSH | Port 22 open to the internet, password and key login |
| Host key | `SHA256:lwqmW+Jl8TFBW+8oAQ7qSVulYLVRhnG/ts3yMmlfU0o` (ED25519) |

### Capacity — action recommended before Phase 1

Each student's stack needs about **0.5–0.6 GB** of disk for images (measured on 2026-11-14 with a minimal app: `postgres:18-alpine` 304 MB, api 164 MB, web 60 MB; the api image grows a little with the real app). Rootless daemons do not share image layers between students. For 13 students that is about **7–8 GB**, plus data, logs and backups. The server has 9.8 GB free today. **It will run out of disk during the project.**

Recommendation: grow the OS disk to at least 64 GB before students reach task P1-T6 (first deployment). Until then, quotas protect students from each other but not the server from all of them together.

Memory: limits are 256 + 256 + 64 MB per student → at most about 7.5 GB for 13 students if every container hits its limit. Measured idle use of a minimal stack: api 96 MiB, db 26 MiB, web 4 MiB, about 130 MiB per student (1.7 GB for 13). Expect 150–250 MiB per student with the real app and some data. This fits. Watch `free -h` in the first week of Phase 2.

### Optional improvements (not required by the plan)

| Improvement | Effect |
|---|---|
| TLS reverse proxy with one sub-domain per student (for example Caddy on 443 → student port) | Removes limits L-1 and L-2 (plain HTTP, shared cookies). Students then set `SESSION_COOKIE_SECURE=true`. |
| Key-only SSH or a login rate limit | Port 22 is open to the internet and accepts passwords. |
| Disk alert | A cron job that mails or posts when `/` is over 85 %. |

## 4. What to check per phase

| Phase | Evidence |
|---|---|
| 0 | Repository exists; environment `production` exists (`gh api repos/<repo>/environments`); issues created |
| 1 | `curl http://spm.iotserver.uz:<port>/api/health` returns `ok` with the SHA of the newest **code** commit on `main` (documents-only commits are not deployed); ruleset `protect-main` active from Phase 0, with required checks from the end of Phase 1; Actions history shows a deploy from a merge |
| 2–5 | Tag exists; the phase's stories work on the live URL; PRs are small, have tests, and the template is filled in |
| 6 | `v1.0.0` release; restore drill report in `docs/STATUS.md`; the student explains the pipeline and one rollback live |

Quick check of all students (ports from your list):

```bash
for p in 11000 11050 11100; do
  printf '%s ' "$p"; curl -s -m 5 "http://spm.iotserver.uz:$p/api/health" || echo "no answer"; echo
done
```

Signs of weak AI-assisted work, visible in the repository: very large PRs, PRs without tests, checks that were disabled, PR descriptions that do not match the diff, documents that no longer match the code.

## 5. Find the student repositories

Students create private repositories in the organisation. Only the student and the organisation owners see them. Students may choose any name. List every repository that was created from the template:

```bash
gh repo list ttpu-spm --limit 200 --json name,createdAt,templateRepository \
  --jq '.[] | select(.templateRepository.name == "SPM-PromptGram-Test") | .name + "  " + .createdAt'
```

## 6. Changing the template

A repository created from the template has no link to it and no common Git history. Students do not receive a template change automatically.

1. Make **one small commit** per change in the template. Avoid changes to `docs/STATUS.md` (every student edits that file, so it conflicts).
2. Announce the commit ID to the class, for example: "Template update `abc1234`: take it with the steps in STUDENT-GUIDE, section *Getting an update of the template*."
3. Students cherry-pick the commit on a branch and merge it with a normal pull request. Students whose repository is older than that section need the commands from you once (they are in the student guide of the template).

Keep the rule: one decision in one place. Requirements in 01, contract in 04, decisions in 10, agent rules in `AGENTS.md`.
