# Prompts

Ready prompts for any AI coding agent (Claude Code, GitHub Copilot agent mode, Codex).

How to use this page:

- **Part A** is the task cycle. Use prompts 1 to 7 **in this order for every task**, then start again with prompt 1 for the next task. This is iterative development: many small, complete cycles.
- **Part B** has the prompts you use once per phase.
- **Part C** has the prompts for when something goes wrong.

Copy a prompt, replace the values in `<...>`, and send it. The prompts are short on purpose: the rules are in `AGENTS.md` and the specification is in `docs/`. The agent reads them; you do not retype them.

Do not skip steps. Do not merge steps into one prompt such as "implement issue 14". Each step has a checkpoint where **you** decide before the agent continues.

---

# Part A — The task cycle (repeat for every task)

```
 ┌──────────────────────────────────────────────────────────────────────────┐
 │  1 Plan → 2 Tests first → 3 Implement → 4 Pull request → 5 Review        │
 │      ↑                                                       ↓           │
 │      └──────── 7 Verify deployment ←── merge ←── 6 Fix findings          │
 └──────────────────────────────────────────────────────────────────────────┘
```

| # | Prompt | Session | Your checkpoint before the next step |
|---|---|---|---|
| 1 | Plan | **New** session | You read the plan and approve or correct it |
| 2 | Tests first | Same session | You read the tests; they fail for the right reason |
| 3 | Implement | Same session | `make check` is green |
| 4 | Pull request | Same session | The PR exists, CI is running |
| 5 | Review | **New** session or a **different** tool | You read the findings and decide which to fix |
| 6 | Fix findings | Session of steps 1–4, or new | CI green; you approve and squash-merge |
| 7 | Verify deployment | Any | The new version is live; the issue is closed |

## 1. Plan (new session, no code yet)

```
We work on issue #<number> (<task id>). Do not write code yet.

1. Read AGENTS.md, the issue, docs/STATUS.md, and the documents the issue names.
2. Give me a plan:
   - the files you will create or change
   - the tests you will write: one or more per acceptance criterion, named after it
     (for example test_fr06_ac3_invalid_title_is_rejected)
   - anything in the docs that is unclear, missing or in conflict with this task
   - any new dependency you think you need, and why
3. Ask me your questions. Then wait for my approval.
```

**Checkpoint:** Does the plan cover every acceptance criterion? Does it stay inside the issue? Answer the questions. Correct the plan now; it is the cheapest moment.

## 2. Tests first

```
The plan is approved<, with these changes: ...>.

1. Create the branch (feat/<number>-<slug>).
2. Write the tests from the plan. Do not write the implementation yet.
3. Run them and show me the result. They must fail because the feature is missing,
   not because of an import or syntax error.
```

**Checkpoint:** Read the tests. Do they check what the acceptance criteria say? A wrong test makes wrong code look right.

## 3. Implement

```
The tests are right. Now write the implementation.

1. Make the tests pass with the simplest code that follows AGENTS.md section 7.
2. Do not change a test to make it pass. If you think a test is wrong, stop and tell me.
3. Run make check (and make e2e if a user journey changed) until everything is green.
4. Show me the final output of make check and a short summary of what you built.
```

**Checkpoint:** `make check` is green in the output (not only in the agent's words). Start the dev stack (`make dev`) and try the feature in the browser.

## 4. Pull request

```
Prepare the pull request.

1. Review your own diff first: remove debug output, dead code and changes this issue did not need.
2. Update docs/STATUS.md, and any document whose content this change made out of date.
3. Push the branch and open a pull request with the template. PR title in Conventional Commit form.
   Fill in every section honestly, including "AI assistance" and the list of
   acceptance criteria with their test names.
4. Give me the PR link. Do not merge.
```

**Checkpoint:** The PR is open. CI started.

## 5. Review (new session, or a different AI tool)

```
Review pull request #<number> as a strict senior reviewer. You did not write this code.

Read AGENTS.md, then the documents that apply (docs/01-requirements.md for the story,
docs/04-api.md, docs/03-data-model.md, docs/07-security.md).

Check, in this order:
1. Tests: does every acceptance criterion have a test that would fail if the behaviour broke?
   Any test without a real assertion? Any test or check that was weakened, skipped or deleted?
2. Contract: do endpoints, fields, status codes and errors match docs/04-api.md exactly?
3. Security: login, CSRF, ownership, validation, file rules, no secrets, no SQL built from strings.
4. Scope: any change that the issue did not ask for? Any new dependency — does it exist and is it needed?
5. Quality: duplication, dead code, unclear names, missing error and empty states, N+1 queries.
6. Docs: are docs/ and docs/STATUS.md updated?

Report findings as a list: severity (blocker / should fix / note), file and line, the problem, the fix.
Do not change code. Do not approve if there is a blocker.
```

**Checkpoint:** Read the findings **and** read the diff yourself (tests first, then code). Decide which findings to fix. You are the reviewer who answers for the merge.

## 6. Fix findings

```
Review findings for PR #<number>. Fix these: <list the findings you accepted>.
Do not fix these, and here is why: <list, or "none">.

1. For each finding: add or correct a test first if the finding shows a missing test, then fix the code.
2. Run make check until green. Push to the same branch.
3. Tell me what changed for each finding.
```

**Checkpoint:** CI is green. No blocker is left. **Squash-merge** the PR yourself. If the fixes were large, run prompt 5 again.

## 7. Verify deployment (after the merge)

```
I merged PR #<number>. The commit on main is <sha>.

1. Watch the pipeline run for this commit with gh until it ends. Tell me the result of each job.
2. If it is green: call http://spm.iotserver.uz:<PORT>/api/health and confirm that "version" is <sha>.
3. If a job failed: read its log, explain the root cause in two or three sentences, and propose a fix.
   Do not change anything yet.
4. Tell me which task comes next according to docs/09-plan.md and docs/STATUS.md.

Note: if the PR changed only documents, the pipeline skips build and deployment. That is correct.
Then confirm only that /api/health still answers "ok".
```

**Checkpoint:** Open the live URL yourself and use the new feature. Close the issue (the PR closes it when it says `Closes #<number>`). Move the card to *Done* on the board.

**Then start the next task with prompt 1 in a new session.**

---

# Part B — Once per phase

## Create the backlog (Phase 0, once)

```
Read AGENTS.md and docs/09-plan.md.

Create the GitHub backlog for this repository with the gh CLI:
1. Labels: phase-1 … phase-6, backend, frontend, infra, docs, human-step.
2. One milestone per phase, named as in "Milestone summary for GitHub" in docs/09-plan.md.
3. One issue per task P1-T1 … P6-T6. Title: "<task id>: <task title>". Body: the task text,
   its "Done when" condition, the story IDs it covers with links to docs/01-requirements.md,
   the documents to read, and a checklist copied from "Definition of done" in AGENTS.md.
   Add the phase label, the area labels, and the milestone. Add human-step to tasks marked as human work.
4. A GitHub Projects board named "PromptGram" owned by the repository owner, linked to this repository,
   with all the issues added (gh project create / link / item-add). If gh reports a missing "project" scope,
   stop and tell me to run: gh auth refresh -s project

Do not create issues for Phase 0. Do not change any file. Show me the list of created issues at the end.
```

## Start of phase

```
We start Phase <n>. Do not write code.

Read AGENTS.md, docs/09-plan.md (Phase <n>), docs/STATUS.md and the stories of this phase in
docs/01-requirements.md.

1. List the tasks of this phase in the order we should do them, with the issue number of each.
2. For each task, name the documents and sections that it needs.
3. Tell me anything in the documents that is unclear or in conflict, before we start.
```

## End of phase check

```
We are at the end of Phase <n>. Read docs/09-plan.md (exit criteria of Phase <n>) and docs/STATUS.md.

1. For each exit criterion, tell me how to verify it, and verify the ones you can
   (tests, CI status with gh, file checks). List the ones only I can verify.
2. Check that every acceptance criterion of this phase's stories maps to a named test. List gaps.
3. Check that the documents match the code. List differences.
Do not change code. Give me a short report.
```

After the report: fix the gaps with normal task cycles, do your own checks, then tag the phase (`git tag v0.<n>.0 && git push origin v0.<n>.0`).

## Security review (Phase 6, different tool or fresh session)

```
Do a security review of the whole repository. You did not write this code.

Read AGENTS.md and docs/07-security.md. Work through the checklist in docs/07-security.md section 6.
Also check: every route in backend/app/api for login, CSRF and ownership; the upload and media code
against the file rules; the Dockerfiles, deploy/compose.yaml, deploy/deploy.sh and the workflows
against docs/05-cicd-and-deployment.md and the container and pipeline rules.

Report findings as a list: severity, file and line, how it could be abused, the fix.
Do not change code. Then propose issues for the findings; I will decide which to create.
```

---

# Part C — When something goes wrong

## Fix a failing pipeline

```
The workflow run <URL or run id> failed. Use gh to read the failing job log.

1. Find the root cause. Explain it to me in two or three sentences before you change anything.
2. Fix the cause, not the symptom. Do not skip, delete or loosen a test or a check.
3. Reproduce locally with the matching make command, then push the fix to the same branch.
```

## Fix a bug

```
Bug: <what happens>. Expected: <what should happen>. Steps: <how to reproduce>.
Do not fix it yet.

1. Write a failing test that reproduces the bug. Show me that it fails.
2. Find the root cause and explain it.
3. After I agree: fix it with the smallest change. Check for the same mistake in similar code.
4. Open a PR (fix/<issue>-<slug>) with the template.
```

Then continue with prompts 5, 6 and 7 of the task cycle.

## Production problem (read-only diagnosis)

```
The app at http://spm.iotserver.uz:<PORT> has a problem: <symptom>.

Help me diagnose it. You may ask me to run read-only commands on the server
(docker compose ps, docker compose logs --tail 100 <service>, cat releases.log, quota -s)
and I will paste the output. Do not ask for commands that change state.
Never ask me for the content of the .env file.
Tell me whether to roll back (deploy workflow with an older image_tag) or to fix forward with a PR.
```

## The agent is stuck (same error three times)

Start a **new** session and send:

```
We are stuck on issue #<number>, branch <branch>. Do not change code yet.

The error is: <paste the full error>.
Already tried, without success: <list>.

1. Read the code and the error. Give me the three most likely root causes, most likely first,
   and how to prove or disprove each one.
2. Wait for me. We test the causes one at a time.
```

## Propose a change to the specification

```
I want to change this: <idea>.

Read the documents it touches. Do not write code. Give me:
1. Which documents and sections change (requirements, API, data model, security, plan).
2. A draft entry for docs/10-decisions.md with alternatives and consequences.
3. The list of tasks it adds, in the format of docs/09-plan.md.
I will decide. If I accept, make the documentation change as its own PR first.
```
