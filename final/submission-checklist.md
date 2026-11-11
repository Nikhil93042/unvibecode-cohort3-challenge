# Official Submission Checklist — UnvibeCode Cohort 3

## General Requirements
- [x] Tested against real public GitHub repositories (`pallets/flask`, `auth0/node-jsonwebtoken`, `encode/starlette`).
- [x] Verified exact versions: UnvibeCode `0.3.15`, Python `3.14.6`, Git `2.55.0.windows.3`, Windows 11 AMD64 (NTFS).
- [x] No private credentials, OpenAI API keys, or proprietary tokens included in any artifact.
- [x] All findings discovered via real execution, decompiled bytecode inspection, and verified logs.

---

## Track 1 Deliverable Checklist
- [x] **Original, Non-Duplicate Issue Discovered**:
  - Issue: Unhandled Windows NTFS file lock collision on `shipreadyv2_pass1_full_results.jsonl` during `atomic_write_text` in Step 03 (`PermissionError: [WinError 5] Access is denied`).
  - Cross-referenced against 530+ issues on `FinanceFlash/unvibecode` (distinct from #463, #467, #445, #456, #525, #494).
- [x] **Required 9-Section GitHub Issue Draft Created**:
  - Fully formatted at `track-1/github-issue-draft.md`.
- [x] **Reproducibility & Evidence**:
  - 100% deterministic minimal reproduction script at `evidence/reproduction/reproduce_file_lock.py` (< 0.1s crash).
  - Raw execution crash log preserved at `evidence/logs/flask_step03_permission_error.log`.
- [x] **Root Cause & Comparative Evidence**:
  - Analyzed the 3 conflicting implementations of `atomic_write` across `customer_runner.py`, `06_...py`, and `03_...py`.
  - Production-ready patch with exponential backoff provided.
- [x] **Human Review Gate**: Issue drafted locally; **ready for user sign-off** before posting to GitHub.

---

## Track 2 Deliverable Checklist
- [x] **Original Product Strategy Formulated**:
  - Concept: *UnvibeCode Differential Guard (`unvibecode diff`)* — two-tier architecture drift engine (sub-2.5s local pre-push AST check + asynchronous GitHub PR Action review).
- [x] **Addresses All Rubric Requirements**:
  - Real repeat usage: Hooks into daily git commit / pre-push / PR cycle.
  - Sub-second time-to-value: < 2.5s local check eliminates slow hook fatigue.
  - Feasibility: Reuses existing `00a` Fast Lane graph and `workflow_selections.json`.
  - Brand recognition & recall: Branded PR comments, SVG diff badges, IDE status bar widget defeat the "invisible MCP" trap.
  - Strict 3-line implementation plan & quantitative retention metrics.
- [x] **Proposal Ready for Form Submission**:
  - Fully formatted at `track-2/final-proposal.md`.

---

## Submission Form Mapping (Google Form)
1. **Candidate Details**: Name, Email, College/Organization, LinkedIn profile.
2. **Track Selection**: Both Track 1 and Track 2.
3. **Analyzed Repository URL**: `https://github.com/pallets/flask` (and `https://github.com/auth0/node-jsonwebtoken`).
4. **Track 1 Issue URL**: *(To be populated upon user approval of GitHub issue filing)*.
5. **Track 1 Summary**: Short summary from `track-1/github-issue-draft.md` Section 1.
6. **Track 2 Proposal**: Text from `track-2/final-proposal.md` Sections 1, 2, and 3.
