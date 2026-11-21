# Student guide — what you do, phase by phase

Your AI agent writes most of the code. This guide lists the steps that **only you** can do: accounts, keys, settings, reviews and decisions.

Marks used below:
- 🧑 **Human only.** Do it yourself. Do not give it to an AI agent (it involves a secret or an account permission).
- 🤖 **Agent can do it.** Give the prompt from [prompts.md](prompts.md).

You need from the teacher: your **server login**, your **server password** and your **port range** (50 ports, for example `11000–11049`). The first port of the range is your `PORT_BASE`. Your app will be at `http://spm.iotserver.uz:<PORT_BASE>`.

---

## Phase 0 — Setup

### 0.1 Install tools on your computer 🧑

You work in **VS Code**. All commands in this guide and in the project are **bash** commands. They do not work in PowerShell or in the Windows command prompt.

| Your computer | Where you type every command |
|---|---|
| **Windows** | The **Ubuntu (WSL 2)** terminal, best inside VS Code (see below). Never PowerShell. |
| **macOS** | The Terminal app, or the terminal inside VS Code. |

**Windows setup (once)**

1. Install WSL 2 with Ubuntu: open PowerShell **as administrator**, run `wsl --install`, restart the PC, and choose a user name and password for Ubuntu. This is the only time you use PowerShell.
2. Install **Docker Desktop**. Then *Settings → Resources → WSL integration* → turn on **Ubuntu**.
3. Install **VS Code** and its extension **WSL** (publisher Microsoft).
4. Open VS Code, press `F1`, run **WSL: Connect to WSL**. The corner at the bottom left now shows `WSL: Ubuntu`. Open a terminal with *Terminal → New Terminal*. This is your Ubuntu terminal.
5. In that terminal, install the tools:
   ```bash
   sudo apt update && sudo apt install -y git gh make
   ```
6. Keep the project inside Ubuntu (for example `~/code/`), **not** under `C:\` or `/mnt/c/`. On `C:` the tools are slow and file watching breaks.

**macOS setup (once)**

1. Install **Docker Desktop** and **VS Code**.
2. Install the tools with Homebrew: `brew install git gh make`.

**All computers**

| Tool | Check (in your bash terminal) |
|---|---|
| Git | `git --version` |
| Docker | `docker compose version` |
| GitHub CLI | `gh auth login` (choose GitHub.com, HTTPS, login with a web browser), then `gh auth status` |
| One AI coding agent: Claude Code, GitHub Copilot (agent mode) or Codex | See 0.8. On Windows, install and run it inside WSL too. |

Docker does not run on your computer (old PC, little memory)? Use a **GitHub Codespace** on your repository instead (Code → Codespaces). Do **not** develop on the SPM server: its disk quota (3 GB) is too small for development tools.

### 0.2 Create your repository from the template 🧑

1. Open the template repository on GitHub. Click **Use this template → Create a new repository**.
2. Owner: `ttpu-spm`. Visibility: **Private**. Leave *Include all branches* off (the template has only `main`). Name: recommended `spm26-promptgram-<your-github-login>`. Another name is fine; nothing in the project depends on the name. The repository is visible to you and to the teacher only.
3. Clone it with VS Code:
   - Windows: first connect to WSL (`F1` → **WSL: Connect to WSL**).
   - Press `F1` → **Git: Clone** → **Clone from GitHub** → sign in when asked → choose your repository → choose the folder `~/code` (create it first with `mkdir -p ~/code`) → **Open**.

   Or clone in the terminal:
   ```bash
   mkdir -p ~/code && cd ~/code
   gh repo clone ttpu-spm/<your-repository>
   code <your-repository>
   ```
4. Check that you see the **Settings** tab of your repository on GitHub. If you do not, you are not an admin of it: ask the teacher.

### 0.3 Check your server account 🧑

```bash
ssh <login>@spm.iotserver.uz
```

The first connection shows the server's key fingerprint. It must be:

```
SHA256:lwqmW+Jl8TFBW+8oAQ7qSVulYLVRhnG/ts3yMmlfU0o   (ED25519)
```

If it is different, stop and tell the teacher. On the server run:

```bash
docker info | grep -i rootless      # must print "rootless"
docker context use rootless         # makes Docker work in non-interactive SSH sessions
quota -s                            # your disk use and limits (3 GB soft, 4 GB hard)
```

### 0.4 Create the deployment SSH key 🧑

This key lets GitHub Actions log in to your server account. It is separate from your own login.

On **your computer** (not on the server), outside the repository folder:

```bash
ssh-keygen -t ed25519 -N "" -C "github-actions-deploy" -f ~/spm-deploy-key
```

This makes two files: `~/spm-deploy-key` (private) and `~/spm-deploy-key.pub` (public).

Install the **public** key on the server, with the `restrict` option in front:

```bash
ssh <login>@spm.iotserver.uz 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
echo "restrict $(cat ~/spm-deploy-key.pub)" | ssh <login>@spm.iotserver.uz 'cat >> ~/.ssh/authorized_keys'
```

Test it. This must print a table header without asking for a password:

```bash
ssh -i ~/spm-deploy-key <login>@spm.iotserver.uz docker ps
```

### 0.5 Create the server `.env` file with your own credentials 🧑

The app reads its settings and passwords from one file on the server: `~/promptgram/.env`. The repository has a template for it: [`deploy/.env.example`](../deploy/.env.example). You copy the template to the server and put in **your own** values. The real file never goes into Git.

1. Copy the template to the server (run this in your repository folder on your computer):
   ```bash
   ssh <login>@spm.iotserver.uz 'mkdir -p ~/promptgram'
   scp deploy/.env.example <login>@spm.iotserver.uz:~/promptgram/.env
   ```
2. Log in to the server and make two random values:
   ```bash
   ssh <login>@spm.iotserver.uz
   openssl rand -hex 24      # use the output as POSTGRES_PASSWORD
   openssl rand -hex 32      # use the output as SECRET_KEY
   ```
3. Open the file and replace both `CHANGE_ME` values:
   ```bash
   nano ~/promptgram/.env    # save: Ctrl+O, Enter   exit: Ctrl+X
   ```
   Leave `IMAGE_REPO`, `IMAGE_TAG` and `WEB_PORT` empty. The pipeline fills them in.
4. Protect the file and check it:
   ```bash
   chmod 600 ~/promptgram/.env
   ls -l ~/promptgram/.env             # must show -rw-------
   grep -c CHANGE_ME ~/promptgram/.env # must print 0
   ```

Rules for this file:

- Use your own random values. Do not reuse a password from another service. Do not share the file.
- Never commit it, and never paste its content into an AI chat, an issue or a PR.
- Do not change `POSTGRES_PASSWORD` after the first deployment. PostgreSQL uses it only when it creates the database.
- If a later PR adds a new variable to `deploy/.env.example`, add the same line to your server file **before** you merge that PR. The PR text tells you.

### 0.6 Create the `production` environment in GitHub 🧑

In your repository: **Settings → Environments → New environment** → name `production`.

1. **Deployment branches and tags:** choose *Selected branches and tags* → add `main`.
2. **Environment secrets → Add secret:**

   | Name | Value |
   |---|---|
   | `DEPLOY_SSH_KEY` | The complete content of the private file `~/spm-deploy-key`, including the `BEGIN` and `END` lines |

3. **Environment variables → Add variable:**

   | Name | Value |
   |---|---|
   | `DEPLOY_HOST` | `spm.iotserver.uz` |
   | `DEPLOY_USER` | your server login |
   | `DEPLOY_PORT_WEB` | your `PORT_BASE` (for example `11000`) |
   | `DEPLOY_KNOWN_HOSTS` | `spm.iotserver.uz ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOkI2LyHNXN2QcSgnt87LJoLxZp3Nt9LYrJ7ErvjycB6` |

The same with the command line (run inside your repository folder):

```bash
gh api -X PUT repos/{owner}/{repo}/environments/production
gh secret set DEPLOY_SSH_KEY --env production < ~/spm-deploy-key
gh variable set DEPLOY_HOST --env production --body "spm.iotserver.uz"
gh variable set DEPLOY_USER --env production --body "<login>"
gh variable set DEPLOY_PORT_WEB --env production --body "<PORT_BASE>"
gh variable set DEPLOY_KNOWN_HOSTS --env production --body "spm.iotserver.uz ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOkI2LyHNXN2QcSgnt87LJoLxZp3Nt9LYrJ7ErvjycB6"
```

(The deployment branch rule is easier to set in the web page.)

Then **delete the private key from your computer**. GitHub has it now, and you do not need it again:

```bash
rm ~/spm-deploy-key ~/spm-deploy-key.pub
```

Never paste the private key into an AI chat, an issue or a file in the repository.

### 0.7 Other repository settings 🧑

- **Settings → Actions → General → Actions permissions:** choose *Allow ttpu-spm, and select non-ttpu-spm, actions and reusable workflows*, then tick **only** *Allow actions created by GitHub*. Leave *Allow Marketplace actions by verified creators* off and the list empty. This project uses GitHub's own actions and nothing else (decision D-21). The same from the command line:
  ```bash
  gh api -X PUT repos/{owner}/{repo}/actions/permissions -F enabled=true -f allowed_actions=selected
  echo '{"github_owned_allowed":true,"verified_allowed":false,"patterns_allowed":[]}' | gh api -X PUT repos/{owner}/{repo}/actions/permissions/selected-actions --input -
  ```
- **Settings → Actions → General → Workflow permissions:** *Read repository contents and packages permissions* (the workflows ask for more where they need it).
- **Settings → General → Pull Requests:** allow **squash merging** only; turn on *Automatically delete head branches*.
- **Protect `main` now.** From this moment nobody, also not your AI agent, can push to `main` directly. Every change goes through a pull request. **Settings → Rules → Rulesets → New branch ruleset:** name `protect-main`, Enforcement **Active**, Target: *Include default branch*. Turn on *Restrict deletions*, *Block force pushes*, *Require linear history*, and *Require a pull request before merging* (required approvals: 0; allowed merge methods: squash only). The same from the command line:
  ```bash
  echo '{"name":"protect-main","target":"branch","enforcement":"active","conditions":{"ref_name":{"include":["~DEFAULT_BRANCH"],"exclude":[]}},"rules":[{"type":"deletion"},{"type":"non_fast_forward"},{"type":"required_linear_history"},{"type":"pull_request","parameters":{"required_approving_review_count":0,"dismiss_stale_reviews_on_push":false,"require_code_owner_review":false,"require_last_push_approval":false,"required_review_thread_resolution":false,"allowed_merge_methods":["squash"]}}]}' | gh api -X POST repos/{owner}/{repo}/rulesets --input -
  ```
  Test it: make a small commit on `main` in your clone and run `git push origin main`. GitHub must reject it. Undo the local commit with `git reset --hard origin/main`. The required status checks come later (step 1.3), when the pipeline exists.
- **Settings → Advanced Security:** turn on *Dependency graph*, *Dependabot alerts* and *Dependabot security updates*. These are free.
- *Secret Protection* (secret scanning, push protection) and *Code Security* (CodeQL code scanning) can cost money on private repositories. Turn them on **only if the teacher told the class to**. If yes: enable Secret Protection with push protection, and Code scanning → **Default setup**.

### 0.8 Connect your AI tool 🧑

| Tool | Steps |
|---|---|
| **Claude Code** | Install it. Run `claude` in the repository folder. It reads `CLAUDE.md` → `AGENTS.md`. Optional: `/install-github-app` so that Claude can answer `@claude` in PRs. |
| **GitHub Copilot** | Sign in to Copilot in VS Code (free with the GitHub Student Developer Pack). Use **Agent** mode in Copilot Chat. It reads `.github/copilot-instructions.md` and `AGENTS.md`. Optional: assign issues to the Copilot coding agent on github.com. |
| **Codex** | Install the Codex CLI or IDE extension. Run `codex` in the repository folder and sign in. It reads `AGENTS.md`. |

Check that it works. Ask your agent: *"What are the hard rules of this repository, and where is the specification?"* It must answer from `AGENTS.md`.

### 0.9 Create the backlog 🤖

Use the prompt **"Create the backlog"** in [prompts.md](prompts.md). The agent creates labels, milestones, issues and a GitHub Projects board from [09-plan.md](09-plan.md) with `gh`. Check the result in the Issues and Projects tabs.

🧑 The board needs one more permission for `gh`. Run this once before the prompt: `gh auth refresh -s project`. In the board, choose the **Board** layout with the columns *Todo*, *In progress*, *Done*, and turn on the built-in workflows *Item closed → Done* and *Pull request merged → Done*.

---

## Phase 1 — Walking skeleton + CI/CD

### 1.1 Run the tasks 🤖 + 🧑
For each task P1-T1 … P1-T7, run the **task cycle**: prompts 1 to 7 of [prompts.md](prompts.md) Part A, in order (Plan → Tests first → Implement → Pull request → Review → Fix findings → Verify deployment). Then start the next task with prompt 1 in a new session. The README (section 7) shows the cycle with an example.

Until task P1-T6 is merged there is no deployment yet: for P1-T1 … P1-T5 the cycle ends after the merge, when CI is green on `main`.

### 1.2 First deployment 🧑
After you merge P1-T6, open **Actions**. Watch `ci` → job `deploy`. When it is green:

- Open `http://spm.iotserver.uz:<PORT_BASE>` in a browser.
- Open `http://spm.iotserver.uz:<PORT_BASE>/api/health`. `version` must be the SHA of your merge commit.
- First deployment only: GitHub → your profile or the organisation → **Packages**. You see `…/api` and `…/web`. They must be **Private**.

If the deploy job fails, read its log and the failure guide in [05-cicd-and-deployment.md](05-cicd-and-deployment.md) section 10. Give the log to your agent.

### 1.3 Add the required checks to the ruleset 🧑
`main` already needs a pull request (step 0.7). Now make a green pipeline a condition for every merge. Do this **after** the first green pipeline run: GitHub offers a check name only after it has run once.

**Settings → Rules → Rulesets → `protect-main` → Edit**

- Turn on *Require status checks to pass* → add `changes`, `backend`, `frontend`, `image` → turn on *Require branches to be up to date before merging*.
- If CodeQL is on for your repository (step 0.7): also turn on *Require code scanning results* → tool CodeQL → security alerts *High or higher*.

Until this step is done, GitHub lets you merge a pull request with red checks. Do not do that: wait for green yourself.

### 1.4 Phase checks 🧑
Do the exit criteria of Phase 1 in [09-plan.md](09-plan.md): second deployment, volume check, manual rollback. Then:

```bash
git checkout main && git pull
git tag v0.1.0 && git push origin v0.1.0
```

---

## Phases 2 to 5 — Features

The same rhythm in every phase:

1. 🤖 Start the phase with the prompt **"Start of phase"** ([prompts.md](prompts.md) Part B).
2. 🤖 + 🧑 For each task: the **task cycle**, prompts 1 to 7, in order. One task per session. Your checkpoints are after each prompt:
   - after *Plan*: approve or correct the plan;
   - after *Tests first*: read the tests;
   - after *Implement*: see `make check` green and try the change on `localhost:5173`;
   - after *Review* (new session or a different tool): read the findings **and** the diff;
   - after *Fix findings*: squash-merge;
   - after *Verify deployment*: use the feature on the server.
   A pull request that changes **only documents** (`docs/`, `*.md`) is not built and not deployed. This is correct. The version on the server stays the same.
3. 🤖 + 🧑 At the end of the phase: prompt **"End of phase check"**, then do the exit criteria in [09-plan.md](09-plan.md), then tag (`v0.2.0`, `v0.3.0`, …).

Things only you can do in these phases:

| Phase | Human step |
|---|---|
| 2 | Register on the server with a **test password** (the site is HTTP, see limit L-1 in [07-security.md](07-security.md)). Create a second account for later tests. |
| 3 | Try **Copy prompt** in a real browser (the clipboard needs a user click). |
| 4 | Upload a real image from your phone. Run `quota -s` on the server after it. |
| 5 | Use two browsers (or one private window) with two accounts to test likes and comments. |

When something breaks in production: do **not** fix it on the server. Either run the `deploy` workflow with the last good SHA (rollback), or fix it with a new PR.

---

## Phase 6 — Hardening and release

| Step | Who |
|---|---|
| Security review with the checklist in [07-security.md](07-security.md) section 6 and the prompt **"Security review"** (Part B) | 🤖 + 🧑 |
| Test on your phone and in a second browser | 🧑 |
| **Restore drill:** copy `deploy/backup.sh` to the server, run it, download the backup with `scp`, restore it into your local dev stack with `deploy/restore.sh`, check that your posts are there. Write date, size and result in `docs/STATUS.md`. | 🧑 |
| README with screenshots and your live URL; `CHANGELOG.md` | 🤖 |
| Tag `v1.0.0`, create the GitHub Release (`gh release create v1.0.0 --generate-notes`) | 🧑 |
| Prepare the demo: live URL, pipeline run, one rollback, answers to the five questions in [08-ai-sdlc.md](08-ai-sdlc.md) section 10 | 🧑 |

---

## Rules for your server account

- Use only your own port range.
- Stay under the disk quota. Check with `quota -s` and `docker system df`. Clean with `docker image prune -af`.
- Never run `docker compose down -v` or `docker volume rm` in `~/promptgram`. That deletes your data.
- Do not edit files in `~/promptgram` by hand. The pipeline owns them.
- The server is shared by the class. Do not run builds, tests or load tests on it.

## Getting an update of the template

Your repository is a copy of the template. It does not follow later changes of the template by itself. When the teacher announces a template update with a commit ID, take it like this:

```bash
git remote add template https://github.com/ttpu-spm/SPM-PromptGram-Test.git   # only the first time
git fetch template
git checkout main && git pull
git checkout -b chore/template-update
git cherry-pick <commit-id-from-the-teacher>
git push -u origin chore/template-update
gh pr create --fill
```

Then merge the pull request as usual.

- If `git cherry-pick` reports a conflict: open the file in VS Code, keep **your** text where you changed the file yourself (for example in `docs/STATUS.md`), keep the **template** text everywhere else, then run `git add -A && git cherry-pick --continue`.
- Use `cherry-pick`, not `git merge`. Your repository and the template have no common history.

## If you lose or leak the deployment key

1. On the server: open `~/.ssh/authorized_keys` and delete the line that ends with `github-actions-deploy`.
2. Repeat steps 0.4 and 0.6 with a new key.

## Getting help

1. Read the error message. Read the failure guide (05, section 10).
2. Ask your agent with the full error text (never with secrets).
3. Ask the teacher. Bring: the link to the failed workflow run, what you tried.
