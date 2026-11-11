Title: [Bug] Pass1FullRunner & CustomerRunner — Unhandled Windows NTFS file lock collision on shipreadyv2_pass1_full_results.jsonl aborts Step 03 review with PermissionError

## 1. Problem summary
During repository reviews on Windows, `Step 03` (`03_shipreadyv2_pass1_full_runner.py`) crashes with an unhandled `PermissionError: [WinError 5] Access is denied` during intermediate result persistence. This failure is caused by an architectural race condition between the parent process's customer progress monitor (`customer_runner.py:907` calling `read_jsonl_quiet`) and the worker process's result persistence (`03_shipreadyv2_pass1_full_runner.py:155` calling `atomic_write_text`).

While `customer_runner.py` explicitly recognizes Windows NTFS file locking for telemetry files and implements a bounded retry loop with unique temporary names (`write_json` lines 271–291), `03_shipreadyv2_pass1_full_runner.py` uses a static `.tmp` filename and directly executes `temporary.replace(path)` without retry backoff or exception handling. When `customer_runner` polls the intermediate results file while `03` is atomically replacing it with newly completed Pass 1 chunk inferences, Windows denies the replacement with `[WinError 5]`.

This aborts the entire Step 03 worker, discards all completed Pass 1 LLM inferences, and terminates the repository review in a crippled `PARTIAL / Needs attention` state with zero Business Workflows and zero Business Risk Findings, completely wasting the developer's time and LLM compute.

## 2. Test environment
- **UnvibeCode version**: `0.3.15` (backed by `shipreadyv2.customer_mvp.v10`)
- **Operating system**: Windows 11 Pro AMD64 (build 10.0.26100, NTFS filesystem)
- **Python version**: Python 3.14.6 (CPython)
- **Git version**: 2.55.0.windows.3
- **Public repository URL and commit**: [pallets/flask](https://github.com/pallets/flask) @ commit `49943b5a94413a530761350f04e896f76e8d620e` (105 files, 194K tokens)
- **Relevant command**:
  ```powershell
  $env:PYTHONIOENCODING="utf-8"
  python -m unvibecode review --repository "C:\test-repos\flask" --no-open-browser
  ```

## 3. Steps to reproduce

> [!NOTE]
> **Platform Prerequisite:** This defect specifically manifests on **Windows (NTFS)** due to Win32 file locking semantics (`MoveFileExW`). On POSIX platforms (Linux/macOS), atomic `rename()` replaces open inodes without locking errors.

### Option A: Real Repository Reproduction (pallets/flask)
1. On Windows 10 or 11, clone `pallets/flask`:
   ```bash
   git clone --depth 1 https://github.com/pallets/flask.git "C:\test-repos\flask"
   ```
2. Execute the official UnvibeCode review command in PowerShell:
   ```powershell
   $env:PYTHONIOENCODING="utf-8"
   python -m unvibecode review --repository "C:\test-repos\flask" --no-open-browser
   ```
3. Observe the CLI output after ~1m 50s. Step 01, Step 02, and all 8 prepared LLM requests complete, but the runner reports:
   ```text
   Business analysis needs attention.
   Reason: Step 03 did not complete. Results that finished successfully were preserved.
   Technical details: ...\technical-logs\business_workflow_review.log
   ! Business analysis: Needs attention
   UNVIBECODE REVIEW PARTIAL · 1m 50s
   ```
4. Inspect the generated technical log:
   `...\unvibecode_results\flask-unvibecode-analysis-*\technical-logs\business_workflow_review.log`
   Observe the fatal traceback ending in:
   `PermissionError: [WinError 5] Access is denied: '...shipreadyv2_pass1_full_results.jsonl.tmp' -> '...shipreadyv2_pass1_full_results.jsonl'`.

### Option B: Deterministic Minimal Reproduction Script (< 1 second)
Run the following self-contained script on Windows simulating `customer_runner.py`'s reader polling and `03_shipreadyv2_pass1_full_runner.py`'s atomic writer:
```python
import os, time, threading
from pathlib import Path

target = Path("./test_results.jsonl")
target.write_text('{"init": true}\n', encoding="utf-8")
stop = threading.Event()

def reader():
    while not stop.is_set():
        try:
            if target.is_file():
                _ = target.read_text(encoding="utf-8").splitlines()
        except Exception:
            pass
        time.sleep(0.005)

def writer():
    tmp = target.with_suffix(".tmp")
    for i in range(100):
        tmp.write_text(f'{{"req": {i}}}\n', encoding="utf-8")
        try:
            tmp.replace(target)
        except PermissionError as exc:
            print(f"[REPRODUCED] Attempt {i}: {exc}")
            stop.set()
            return
        time.sleep(0.01)

t_r = threading.Thread(target=reader)
t_w = threading.Thread(target=writer)
t_r.start(); t_w.start()
t_w.join(); stop.set(); t_r.join()
target.unlink(missing_ok=True)
Path("./test_results.tmp").unlink(missing_ok=True)
```
Output on Windows:
```text
[REPRODUCED] Attempt 0: [WinError 5] Access is denied: 'test_results.tmp' -> 'test_results.jsonl'
```

## 4. Expected behavior
1. As stated in `shipreadyv2/customer_runner.py` lines 64–67:
   `"Progress and status JSON files use unique temporary names and bounded retry backoff for transient Windows file locks."`
2. Result persistence in `03_shipreadyv2_pass1_full_runner.py` (`atomic_write_text` / `persist_results`) must adhere to this exact resilience contract:
   - It should generate unique temporary filenames (e.g. `.{path.name}.{pid}.{ns}.tmp`) rather than a fixed collision-prone `.tmp` name.
   - It must implement a retry loop with exponential backoff catching `OSError` (specifically `WinError 5` / `EACCES`).
3. Step 03 should complete smoothly, and the review should proceed to Step 04 (Business Path Compiler), Step 05 (Insight Selector), and Step 06 (Risk Findings Review), producing complete Business Workflow Maps and Risk Findings.

## 5. Actual behavior
1. `03_shipreadyv2_pass1_full_runner.py` successfully completes all 8 LLM analysis requests, but crashes during `persist_results` after request 8 completes:
   ```text
   Traceback (most recent call last):
     File "C:\Users\...\shipreadyv2\customer_runner.py", line 1759, in run_full_analysis_worker
       run_step_three(module, report_folder, engine_root)
     File "C:\Users\...\shipreadyv2\customer_runner.py", line 1630, in run_step_three
       call_main(module, "Step 03")
     File "C:\Users\...\shipreadyv2\customer_runner.py", line 1043, in call_main
       normalize_return_code(main_function(), stage_name)
     File "03_shipreadyv2_pass1_full_runner.py", line 1430, in main
       failures = run_requests_in_parallel(...)
     File "03_shipreadyv2_pass1_full_runner.py", line 1312, in run_requests_in_parallel
       persist_results(RESULTS_JSONL_PATH, selected_requests, completed)
     File "03_shipreadyv2_pass1_full_runner.py", line 1008, in persist_results
       atomic_write_jsonl(path, ordered)
     File "03_shipreadyv2_pass1_full_runner.py", line 168, in atomic_write_jsonl
       atomic_write_text(path, text)
     File "03_shipreadyv2_pass1_full_runner.py", line 159, in atomic_write_text
       temporary.replace(path)
   PermissionError: [WinError 5] Access is denied: 'C:\...\shipreadyv2_pass1_full_results.jsonl.tmp' -> 'C:\...\shipreadyv2_pass1_full_results.jsonl'
   ```
2. The entire Business Analysis pipeline aborts with `PARTIAL / Needs attention`.
3. The customer receives zero Business Workflows and zero Business Risk Findings.

## 6. Evidence

### Codebase Inconsistency: 3 Conflicting Atomic Write Implementations
A forensic inspection of the codebase reveals that atomic file persistence was implemented three separate times across the pipeline with conflicting levels of resilience:

1. **`customer_runner.py:271–291` (`write_json`) — Fully Hardened with Backoff**:
   ```python
   # A fixed `file.json.tmp` is vulnerable to antivirus/indexer locks and to
   # overlapping refreshes on Windows. Every attempt gets a unique name.
   for attempt in range(7):
       temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
       try:
           temporary.write_text(serialized, encoding="utf-8", newline="\n")
           os.replace(temporary, path)
           return True
       except OSError:
           try:
               temporary.unlink(missing_ok=True)
           except OSError:
               pass
           if attempt < 6:
               time.sleep(min(0.8, 0.025 * (2**attempt)))
   ```
2. **`06_shipreadyv2_step4_v2_with_v4_inputs.py:232–244` (`atomic_write_text`) — Unique Name via mkstemp, but No Retry Loop**:
   ```python
   def atomic_write_text(path: Path, text: str) -> None:
       path.parent.mkdir(parents=True, exist_ok=True)
       fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
       try:
           with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
               handle.write(redact_artifact(path.name, text.encode("utf-8")).decode("utf-8"))
               handle.flush()
               os.fsync(handle.fileno())
           os.replace(temporary, path)
       finally:
           if os.path.exists(temporary):
               os.unlink(temporary)
   ```
3. **`03_shipreadyv2_pass1_full_runner.py:155–160` (`atomic_write_text`) — Unhardened, Collides on Static `.tmp`, Zero Retries (BUG)**:
   ```python
   def atomic_write_text(path: Path, text: str) -> None:
       path.parent.mkdir(parents=True, exist_ok=True)
       temporary = path.with_suffix(path.suffix + ".tmp")
       temporary.write_text(redact_artifact(path.name, text.encode("utf-8")).decode("utf-8"), encoding="utf-8", newline="\n")
       temporary.replace(path)  # Fatal WinError 5 here
   ```

### Execution Log Excerpt
From `unvibecode_results/flask-unvibecode-analysis-20261106_123405/technical-logs/business_workflow_review.log`:
```text
[SHIPREADYV2 PASS 1 INPUT PREPARATION COMPLETE]
Semantic packs:  4
LLM requests:    8
Requests per semantic pack:
  semantic_pack_001: 2
  semantic_pack_002: 2
  semantic_pack_003: 1
  semantic_pack_004: 3
...
[7/8] DONE semantic_pack_004_part_02 in 9.9s | input=50065, cached=6579, output=1050, reasoning=138 | paths=0, facts=0, evidence=4
[8/8] START semantic_pack_004_part_03 | attempt=1/2, input=55,940, reasoning=low, max_output=32,000
[8/8] DONE semantic_pack_004_part_03 in 11.2s | input=63021, cached=6579, output=844, reasoning=92 | paths=0, facts=0, evidence=6

Traceback (most recent call last):
  File "C:\Users\HP\AppData\Roaming\Python\Python314\site-packages\shipreadyv2\customer_runner.py", line 1759, in run_full_analysis_worker
    run_step_three(module, report_folder, engine_root)
  File "C:\Users\HP\AppData\Roaming\Python\Python314\site-packages\shipreadyv2\customer_runner.py", line 1630, in run_step_three
    call_main(module, "Step 03")
  File "C:\Users\HP\AppData\Roaming\Python\Python314\site-packages\shipreadyv2\customer_runner.py", line 1043, in call_main
    normalize_return_code(main_function(), stage_name)
  File "03_shipreadyv2_pass1_full_runner.py", line 1430, in main
    failures = run_requests_in_parallel(...)
  File "03_shipreadyv2_pass1_full_runner.py", line 1312, in run_requests_in_parallel
    persist_results(RESULTS_JSONL_PATH, selected_requests, completed)
  File "03_shipreadyv2_pass1_full_runner.py", line 1008, in persist_results
    atomic_write_jsonl(path, ordered)
  File "03_shipreadyv2_pass1_full_runner.py", line 168, in atomic_write_jsonl
    atomic_write_text(path, text)
  File "03_shipreadyv2_pass1_full_runner.py", line 159, in atomic_write_text
    temporary.replace(path)
PermissionError: [WinError 5] Access is denied: 'C:\...\shipreadyv2_pass1_full_results.jsonl.tmp' -> 'C:\...\shipreadyv2_pass1_full_results.jsonl'
```

## 7. Impact and scope
- **Affected Audience**: All developers executing UnvibeCode on Windows operating systems (the platform explicitly documented in `README.md` and `docs/QUICKSTART.md`).
- **Severity**: Critical review abort. The tool crashes after spending substantial runtime (~2 minutes) and hosted AI tokens executing all 8 Pass 1 semantic skimming requests, yet produces zero business workflows and zero risk findings.
- **Scope**: Triggered on any repository with multiple Pass 1 semantic chunks because `persist_results` is called repeatedly after every completed request while the parent runner's progress dashboard actively polls `shipreadyv2_pass1_full_results.jsonl`.

## 8. Suspected cause / suggested fix (if known)

### Root Cause
Under Windows NTFS semantics, `os.replace(src, dst)` invokes the Win32 API `MoveFileExW` with `MOVEFILE_REPLACE_EXISTING`. If another process (here, `customer_runner.py:read_jsonl_quiet`) currently has `dst` open for reading without `FILE_SHARE_DELETE` (which CPython's standard `open()` / `Path.read_text()` does not specify), Windows locks the file from being replaced and returns `ERROR_ACCESS_DENIED` (`WinError 5`). 

Because `03_shipreadyv2_pass1_full_runner.py:atomic_write_text` uses a non-unique static temporary name (`.tmp`) and executes `temporary.replace(path)` directly with no retry loop, this transient collision becomes an unhandled fatal exception.

### Suggested Fix
Refactor `atomic_write_text` in `03_shipreadyv2_pass1_full_runner.py` (and `06_shipreadyv2_step4_v2_with_v4_inputs.py`) to adopt the Windows-safe retry pattern already implemented in `customer_runner.py:write_json`:

```python
import os, time

def atomic_write_text(path: Path, text: str, max_attempts: int = 7) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    screened = redact_artifact(path.name, text.encode("utf-8")).decode("utf-8")
    for attempt in range(max_attempts):
        temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
        try:
            temporary.write_text(screened, encoding="utf-8", newline="\n")
            os.replace(temporary, path)
            return
        except OSError:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            if attempt < max_attempts - 1:
                time.sleep(min(0.8, 0.025 * (2**attempt)))
            else:
                raise
```

## 9. Duplicate check
Checked against all 530+ open and closed issues in `FinanceFlash/unvibecode`:
- **#463**: `[Bug] CustomerDashboardRenderer — UnicodeEncodeError on cp1252/Windows consoles when rendering progress status bullets ('\u25cf')`. Issue #463 covers console terminal stdout character encoding on Windows. It does not address the concurrent filesystem lock collision between `read_jsonl_quiet` and `atomic_write_text` in Step 03.
- **#467**: `[Bug] Business Path Compiler (Step 04) — a contract-valid NO_MATERIAL_PATH Pass 1 result aborts the whole review as PARTIAL/FAILED`. Issue #467 covers Step 04 compiler aborting when Pass 1 yields no material paths. This bug occurs in Step 03 during file persistence before Step 04 is even reached.
- **#445**: `[Bug] Completed context export — COMPLETE reviews attach findings to contradictory source versions`. Issue #445 addresses commit hash provenance verification in ZIP export.
- **#456**: `[Bug] Code Understanding — one deeply nested file raises RecursionError`. Issue #456 addresses recursion limits in Fast Lane graph resolution.
- **#525**: `[Bug] Fast Lane context export: UTF-8 BOM on a source file becomes line 1 content`. Addresses BOM stripping in context preparation.
- **#494**: `[Bug] Code understanding — JavaScript export clause syntax error`. Addresses TreeSitter parsing for export clauses.
- **Result**: Zero duplicate issues exist for this Windows NTFS file lock race condition.
