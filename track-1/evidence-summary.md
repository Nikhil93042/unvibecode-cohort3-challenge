# Track 1 — Evidence and Reproduction Summary

## 1. Verified Defect Matrix

| Item | Verified Value | Evidence Location |
| :--- | :--- | :--- |
| **Defect Name** | Unhandled Windows NTFS file lock collision during Step 03 result persistence (`PermissionError: [WinError 5] Access is denied`) | `track-1/github-issue-draft.md` |
| **Failing Component** | `shipreadyv2/engine_sources/03_shipreadyv2_pass1_full_runner.py:155–160` (`atomic_write_text`) | `03_shipreadyv2_pass1_full_runner.py` |
| **Colliding Reader** | `shipreadyv2/customer_runner.py:902–908` (`read_jsonl_quiet`) in parent process progress display | `customer_runner.py` |
| **Target Repository** | `pallets/flask` @ commit `49943b5a94413a530761350f04e896f76e8d620e` | `C:\test-repos\flask` |
| **Tested Scale** | 105 files, 391 chunks, 4 semantic packs, 8 prepared LLM requests | `flask_step03_permission_error.log` |
| **Crash Point** | Immediately following Request [8/8] completion during `persist_results` | Line 198 of `flask_step03_permission_error.log` |
| **Reproduction Script** | Self-contained Python script reproducing in < 0.1s on Windows | `evidence/reproduction/reproduce_file_lock.py` |
| **Reproduction Reliability**| 100% deterministic on Windows NTFS (10/10 runs reproduced on Attempt 0 or 1) | `evidence/reproduction/reproduce_file_lock.py` |
| **Non-Duplicate Status** | Confirmed 0 duplicate issues across all 530+ issues in `FinanceFlash/unvibecode` | `track-1/github-issue-draft.md` Section 9 |

---

## 2. Three-Way Codebase Architecture Comparison

| Source File | Function | Temp File Naming | Retry Logic | WinError 5 Vulnerability |
| :--- | :--- | :--- | :--- | :--- |
| **`customer_runner.py:271–291`** | `write_json` | `.{name}.{pid}.{ns}.tmp` (Unique per PID/nano) | 7 attempts with exponential backoff (`0.025 * 2^attempt`) | **Immune (Properly Hardened)** |
| **`06_shipreadyv2_step4_...py:232`** | `atomic_write_text` | `tempfile.mkstemp(prefix=f".{name}.")` | Zero retry on `os.replace` | Vulnerable if reader locks destination |
| **`03_shipreadyv2_pass1_...py:155`** | `atomic_write_text` | `name + ".tmp"` (Static non-unique suffix) | **Zero retry / Zero backoff** | **Critically Vulnerable (CRASHES)** |

---

## 3. Real Repository Test Records

1. **`pallets/flask` (Python)**:
   - Command: `python -m unvibecode review --repository C:\test-repos\flask --no-open-browser`
   - Outcome: **CRASH** at Step 03 with `PermissionError: [WinError 5]` (Raw log preserved in `evidence/logs/flask_step03_permission_error.log`).
2. **`auth0/node-jsonwebtoken` (JavaScript/TypeScript)**:
   - Command: `python -m unvibecode review --repository C:\test-repos\node-jsonwebtoken --no-open-browser`
   - Outcome: **SUCCESS** (2m 41s). Generated all 4 HTML outputs + ZIP context. Preserved in `unvibecode_results/node-jsonwebtoken-unvibecode-analysis-20261106_122636/`.
3. **`encode/starlette` (Python)**:
   - Command: `python -m unvibecode review --repository C:\test-repos\starlette --no-open-browser`
   - Outcome: Encountered known console encoding bug (#463) on Windows `cp1252` when rendering `\u25cf`. Resolved by passing `$env:PYTHONIOENCODING="utf-8"`.
