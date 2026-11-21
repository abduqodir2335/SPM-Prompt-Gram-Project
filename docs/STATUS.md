# Status

Progress tracker and shared memory between sessions and tools.
The agent updates this file in every PR that finishes a task. Keep entries short.

**Current phase:** 0 — Setup
**Live URL:** `http://spm.iotserver.uz:<PORT_BASE>` (fill in after step 0.3)
**Last deployed version:** —

## Tasks

Mark a task `[x]` in the PR that finishes it and add the PR number.

### Phase 0 — Setup
- [ ] P0-T1 Tools installed; repository created from the template
- [ ] P0-T2 Server account and rootless Docker checked
- [ ] P0-T3 Deployment SSH key created and installed
- [ ] P0-T4 Server `.env` created from `deploy/.env.example`
- [ ] P0-T5 Environment `production` with secret and variables
- [ ] P0-T6 Repository settings done; AI tool connected
- [ ] P0-T7 Backlog and Projects board created

### Phase 1 — Walking skeleton + CI/CD (`v0.1.0`)
- [ ] P1-T1 Backend skeleton
- [ ] P1-T2 Frontend skeleton
- [ ] P1-T3 Dev stack
- [ ] P1-T4 Production images + first e2e test
- [ ] P1-T5 CI workflow
- [ ] P1-T6 Deployment
- [ ] P1-T7 Backup and restore scripts
- [ ] P1-T8 `main` protected

### Phase 2 — Authentication (`v0.2.0`)
- [ ] P2-T1 User model + migration
- [ ] P2-T2 Auth API
- [ ] P2-T3 Frontend API client + auth state
- [ ] P2-T4 Login and register pages, header
- [ ] P2-T5 e2e: auth journey

### Phase 3 — Posts, feed, profile (`v0.3.0`)
- [ ] P3-T1 Post model + migration
- [ ] P3-T2 Posts API: create, get, list
- [ ] P3-T3 Posts API: edit, delete; users API
- [ ] P3-T4 Feed page
- [ ] P3-T5 Create and edit post pages
- [ ] P3-T6 Post detail page with Copy prompt
- [ ] P3-T7 Profile page
- [ ] P3-T8 e2e: post journey; demo seed command

### Phase 4 — Attachments (`v0.4.0`)
- [ ] P4-T1 Attachment model + storage service
- [ ] P4-T2 Attachments API
- [ ] P4-T3 File input in the post form
- [ ] P4-T4 Show attachments
- [ ] P4-T5 e2e: attachment journey

### Phase 5 — Likes and comments (`v0.5.0`)
- [ ] P5-T1 Likes model + API
- [ ] P5-T2 Comments model + API
- [ ] P5-T3 Like button
- [ ] P5-T4 Comments UI
- [ ] P5-T5 e2e: social journey

### Phase 6 — Hardening and release (`v1.0.0`)
- [ ] P6-T1 Security review
- [ ] P6-T2 Accessibility and responsive pass
- [ ] P6-T3 Performance check
- [ ] P6-T4 Restore drill
- [ ] P6-T5 Documentation
- [ ] P6-T6 Release

## Notes for the next session

Things a new session must know that are not in the other documents: open problems, things tried that did not work, decisions waiting for the human. Delete a note when it is no longer true.

- (none yet)

## Restore drill report (Phase 6)

| Date | Backup size | Restored into | Result |
|---|---|---|---|
| | | | |
