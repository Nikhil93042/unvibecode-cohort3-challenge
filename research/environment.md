# UnvibeCode Cohort 3 — Test Environment Specification

## System Environment
- **Operating System**: Microsoft Windows 11 Home / Pro (AMD64, 64-bit)
- **PowerShell Version**: 5.1 / Core
- **Available Disk Space**: ~119.68 GB free on C:\
- **Current Timestamp**: 2026-11-06T12:19:35+05:30

## Tooling & Runtime
- **Python**: 3.14.6 (`python --version` confirmed: `Python 3.14.6`)
  - Python Executable Path: Detected in `%LOCALAPPDATA%\Programs\Python\Python314\python.exe`
  - Site Packages Path: `C:\Users\HP\AppData\Roaming\Python\Python314\site-packages`
- **Git**: 2.55.0.windows.3 (`git --version` confirmed: `git version 2.55.0.windows.3`)

## UnvibeCode Installation & Identity
- **Package Name**: `unvibecode`
- **Installed Version**: `0.3.15`
- **License**: Mixed model (Apache 2.0 / LicenseRef-Proprietary)
- **Dependencies**: `jsonschema`, `openai`, `pyvis`, `PyYAML`, `tiktoken`, `tinycss2`, `tree-sitter-language-pack`
- **Underlying Implementation**: `shipreadyv2` (version `shipreadyv2.customer_mvp.v10`)
- **CLI Commands Available**:
  - `python -m unvibecode --help`
  - `python -m unvibecode review --repository "/path/to/repo"`
- **Hosted API Endpoint**: `https://shipready-api.alphashots.ai/v1`
- **Token Mode**: Narrow public preview token (`unvibecode-public-preview-v1`)

## CLI Verification
```text
$ python -m unvibecode --help
usage: unvibecode [-h] [--version] {review} ...

Create a connected code map and, when repository size permits, a business
workflow and risk review.

positional arguments:
  {review}
    review    Review a source repository

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```