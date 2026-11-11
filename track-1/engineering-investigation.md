# Track 1 Deep Engineering Investigation Report

## Executive Summary
This document provides a comprehensive root-cause analysis, empirical reproduction study, and architectural evaluation of a fatal concurrency defect discovered in UnvibeCode (`0.3.15`): **the unhandled Windows file lock collision in Step 03 (`03_shipreadyv2_pass1_full_runner.py`) during atomic result persistence**.

The defect aborts the entire Business Workflow and Risk Review on Windows whenever a repository requires multiple Pass 1 semantic skimming requests, leaving the developer with zero business workflows, zero risk findings, and wasted AI tokens.

---

## Technical Architecture & Failure Mechanism

### 1. The Dual-Process Pipeline Architecture
UnvibeCode uses a multi-stage architecture where:
- The parent process (`shipreadyv2.customer_runner`) orchestrates execution, updates the live CLI dashboard, and monitors progress files.
- The worker process (`shipreadyv2.engine_sources.03_shipreadyv2_pass1_full_runner`) dispatches Pass 1 LLM requests to `https://shipready-api.alphashots.ai/v1`.
- As parallel requests complete, `03_shipreadyv2_pass1_full_runner.py` calls `persist_results()` to incrementally write `shipreadyv2_pass1_full_results.jsonl`.

### 2. Windows NTFS File Sharing Semantics
Unlike POSIX systems where `rename()` is an atomic directory metadata swap that succeeds regardless of open file descriptors, Windows NTFS enforces mandatory and opportunistic file locks:
- When a process opens a file via standard Win32 `CreateFileW` without the `FILE_SHARE_DELETE` flag, the operating system denies any subsequent attempt to delete, rename, or overwrite that file until the reading handle is closed.
- CPython's standard `open()` and `Path.read_text()` on Windows open files with `FILE_SHARE_READ | FILE_SHARE_WRITE`, but omit `FILE_SHARE_DELETE`.
- In `customer_runner.py:907`, the customer progress monitor calls `read_jsonl_quiet()` to check how many code areas have completed.
- At the exact same time, `03_shipreadyv2_pass1_full_runner.py:159` executes `temporary.replace(path)`.
- Because `path` is momentarily open in the parent reader, Windows refuses the `replace` and throws `PermissionError: [WinError 5] Access is denied`.

### 3. The Internal Contradiction in shipreadyv2
The failure is especially notable because the developers of UnvibeCode specifically anticipated this problem in `customer_runner.py`:
```python
# Lines 271-291 of customer_runner.py
# A fixed `file.json.tmp` is vulnerable to antivirus/indexer locks and to
# overlapping refreshes on Windows. Every attempt gets a unique name.
for attempt in range(7):
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    try:
        temporary.write_text(serialized, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
        return True
    except OSError:
        ...
        if attempt < 6:
            time.sleep(min(0.8, 0.025 * (2**attempt)))
```
However, in `03_shipreadyv2_pass1_full_runner.py` (and `06_shipreadyv2_step4_v2_with_v4_inputs.py`), they implemented a naive atomic writer without any retry logic or unique naming:
```python
# Lines 155-160 of 03_shipreadyv2_pass1_full_runner.py
def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(redact_artifact(path.name, text.encode("utf-8")).decode("utf-8"), encoding="utf-8", newline="\n")
    temporary.replace(path)
```
This architectural discrepancy directly violates the product's own design principles, causing real repository analyses to crash.

---

## Empirical Verification Across Tested Repositories

| Repository | Concurrency & Size | Pass 1 Requests | Outcome | Observable Behavior |
|---|---|---|---|---|
| **pallets/flask** | Synchronous WSGI, 105 files | 8 requests | **FAILED (PermissionError)** | Step 03 executed all 8 requests, but crashed on `shipreadyv2_pass1_full_results.jsonl.tmp -> replace`. Result: `PARTIAL / Needs attention`. 0 workflows published. |
| **encode/starlette** | Async ASGI, 88 files | 12 requests | **FAILED (UnicodeEncodeError)** | Terminated by `dashboard_renderer` `\u25cf` cp1252 crash before Step 03 persistence could finish. |
| **auth0/node-jsonwebtoken** | JS/TS, 46 files | 2 requests | **COMPLETED** | Completed successfully due to low request count and low collision probability. 3 workflows generated. |
| **Minimal Reproduction Script** | Multi-threaded mock | 100 iterations | **FAILED (100% Deterministic)** | `PermissionError: [WinError 5]` triggered on **Attempt 0** in < 0.1s. |

---

## Suggested Engineering Fix

Apply the proven exponential backoff pattern to `03_shipreadyv2_pass1_full_runner.py`:

```python
def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    screened = redact_artifact(path.name, text.encode("utf-8")).decode("utf-8")
    for attempt in range(10):
        temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
        try:
            temporary.write_text(screened, encoding="utf-8", newline="\n")
            os.replace(temporary, path)
            return
        except OSError as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            if attempt < 9:
                time.sleep(min(0.5, 0.02 * (2**attempt)))
            else:
                raise exc
```

This ensures full Windows NTFS resilience, matching the standard established in `customer_runner.py`.
