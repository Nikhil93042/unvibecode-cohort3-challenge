# UnvibeCode Cohort 3 — Engineering Investigation Log

## Timeline of Real Engineering Actions & Empirical Findings

### Step 1: Environment & Tooling Verification
- Executed: `python --version`, `git --version`, `Get-PSDrive`
- Observed: Python 3.14.6, Git 2.55.0.windows.3, ~119.68 GB free disk space on Windows 11 AMD64.
- Inspected installed package: `unvibecode` version `0.3.15` (Location: `C:\Users\HP\AppData\Roaming\Python\Python314\site-packages\unvibecode`).
- Identified underpinning engine: `shipreadyv2` (version `shipreadyv2.customer_mvp.v10`).

### Step 2: Repository Selection & Test Harness
- Cloned three public repositories pegged to immutable commit hashes:
  1. `encode/starlette` (`0f08970e5cce0aec4fc1cea7447c262d741795eb`) — 88 files, ~263K tokens.
  2. `pallets/flask` (`49943b5a94413a530761350f04e896f76e8d620e`) — 105 files, ~194K tokens.
  3. `auth0/node-jsonwebtoken` (`b924272f29192e12926b5414546f7c5bfcc9579d`) — 46 files, ~49K tokens.

### Step 3: Empirical Execution on Starlette & Initial Windows Failure Discovery
- Executed: `python -m unvibecode review --repository "C:\Users\HP\Downloads\test-repos\starlette" --no-open-browser`
- Result: Fast Lane completed in 8.628s.
- Pass 1 LLM requests 1–7 succeeded, but execution crashed at the live terminal renderer:
  `UnicodeEncodeError: 'charmap' codec can't encode character '\u25cf' in position 2: character maps to <undefined>`
- Root Cause: `dashboard_renderer.render` in `customer_runner.py:685` attempted to print progress bullets (`\u25cf`) to a Windows console defaulting to `cp1252`.
- Duplicate check: Issue #463 was already open for this specific console UnicodeEncodeError.
- Remediation applied for testing: `$env:PYTHONIOENCODING="utf-8"` enabled subsequent runs to proceed.

### Step 4: Empirical Execution on node-jsonwebtoken (Full Review Success)
- Executed: `$env:PYTHONIOENCODING="utf-8"; python -m unvibecode review --repository "C:\Users\HP\Downloads\test-repos\node-jsonwebtoken" --no-open-browser`
- Execution duration: 2m 41s.
- Result: Full success (Code understanding + Business analysis).
- Outputs produced:
  - `00_unvibecode_results.html` (Landing Dashboard)
  - `connected-code.html` (776 KB interactive graph)
  - `business-workflows.html` (3 workflows identified: Decode JWT, Sign JWT, Verify JWT)
  - `risk-findings.html` (0 evidence-supported risks met reporting ceiling)
  - `node-jsonwebtoken-repository-context.zip` (Complete repository context including `manifest.json`, `chunks.jsonl`, `connections.jsonl`, `selections.jsonl`, `workflow_context.md`)

### Step 5: Empirical Execution on Flask & Discovery of Critical Windows Race Condition
- Executed: `$env:PYTHONIOENCODING="utf-8"; python -m unvibecode review --repository "C:\Users\HP\Downloads\test-repos\flask" --no-open-browser`
- Codebase size: ~194,479 tokens across 105 source files; 8 Pass 1 LLM requests generated.
- Progress: Fast Lane completed in 6.424s. Requests 1–7 completed successfully over 1m 50s.
- Fatal failure occurred during intermediate result persistence at request 8:
  ```text
  File "C:\Users\HP\AppData\Local\Temp\unvibecode-engine-...\engine\03_shipreadyv2_pass1_full_runner.py", line 1430, in main
    failures = run_requests_in_parallel(...)
  File "03_shipreadyv2_pass1_full_runner.py", line 1312, in run_requests_in_parallel
    persist_results(RESULTS_JSONL_PATH, selected_requests, completed)
  File "03_shipreadyv2_pass1_full_runner.py", line 1008, in persist_results
    atomic_write_jsonl(path, ordered)
  File "03_shipreadyv2_pass1_full_runner.py", line 168, in atomic_write_jsonl
    atomic_write_text(path, text)
  File "03_shipreadyv2_pass1_full_runner.py", line 159, in atomic_write_text
    temporary.replace(path)
  PermissionError: [WinError 5] Access is denied: '...shipreadyv2_pass1_full_results.jsonl.tmp' -> '...shipreadyv2_pass1_full_results.jsonl'
  ```
- Final review status: `UNVIBECODE REVIEW PARTIAL · 1m 50s`. `Step 03 did not complete`. Zero business workflows or risk findings published.

### Step 6: Root Cause Investigation & Minimal Reproduction
- Analyzed `customer_runner.py` vs `03_shipreadyv2_pass1_full_runner.py`:
  - `customer_runner.py:907` runs `read_jsonl_quiet(report_folder / "shipreadyv2_pass1_full_results.jsonl")` every progress cycle to calculate completed code areas (`complete of total code areas reviewed`).
  - `customer_runner.py:597–610` opens the file via `path.read_text(encoding="utf-8")`.
  - On Windows NTFS, standard `open()` does not grant `FILE_SHARE_DELETE`.
  - Meanwhile, `03_shipreadyv2_pass1_full_runner.py:155–160` executes `temporary.replace(path)` using a hardcoded `.tmp` extension without retries, error handling, or sharing tolerance.
  - The developer explicitly recognized this in `customer_runner.py:271–291` (`# A fixed file.json.tmp is vulnerable to antivirus/indexer locks and to overlapping refreshes on Windows`) and wrote a 7-attempt exponential backoff retry loop for telemetry. But they neglected to apply this pattern to the engine scripts (`03_shipreadyv2_pass1_full_runner.py` and `06_shipreadyv2_step4_v2_with_v4_inputs.py`).
- Constructed standalone test `reproduce_file_lock.py` simulating concurrent reader polling and writer replacement.
- Result: **PermissionError reproduced deterministically on Attempt 0 in < 0.1s**.
- Preserved reproduction script and crash logs in `evidence/`.

### Step 7: Duplicate Elimination & Verification
- Queried GitHub API for all open and closed issues on `FinanceFlash/unvibecode` (#1 to #533+).
- Verified zero duplicate issues reporting Windows file lock collisions or `PermissionError` in `atomic_write_text`.