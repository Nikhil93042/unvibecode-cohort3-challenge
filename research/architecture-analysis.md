# UnvibeCode Architecture & Execution Engine Analysis

## High-Level Architecture Overview

UnvibeCode transforms a codebase into 4 interconnected outputs without requiring customer OpenAI API keys or credentials. It operates as a hybrid local/remote engine:
- **Local Stage**: File discovery, deterministic size estimation, AST extraction (Python AST and Tree-sitter), static graph construction, chunking, symbol linking, credential redaction, and local HTML visualization.
- **Hosted Stage**: Semantic business workflow reconstruction, capability naming, universal insight selection, and flaw synthesis via hosted GPT models (`gpt-5.4-mini` and `gpt-5.4`).

```
                    ┌─────────────────────────┐
                    │ Customer CLI Invocation │
                    │ python -m unvibecode    │
                    └────────────┬────────────┘
                                 │
                   ┌─────────────▼─────────────┐
                   │ Preflight & Size Estimate │
                   │  (2M source token cutoff) │
                   └─────────────┬─────────────┘
                                 │
           ┌─────────────────────┴─────────────────────┐
           ▼                                           ▼
┌────────────────────────┐                 ┌────────────────────────┐
│   Track A (Fast Lane)  │                 │ Track B (Business Lane)│
│  00a_fast_lane_v11.py  │                 │ Steps 01 to 06 Pipeline│
└──────────┬─────────────┘                 └───────────┬────────────┘
           │                                           │
           │ • AST Symbol Graph                        │ • Step 01: Merged Graph
           │ • Token Chunks (5 chunks)                 │ • Step 02: Prepare Pass 1
           │ • 01_connected_code_map.html              │ • Step 03: Pass 1 LLM
           │ • Context Selections                      │ • Step 04: Path Compiler
           │                                           │ • Step 05: Insight Selector
           │                                           │ • Step 06: Risk Flaw Review
           │                                           │ • 02_business_workflow.html
           │                                           │ • 03_risk_findings.html
           └─────────────────────┬─────────────────────┘
                                 │
                   ┌─────────────▼─────────────┐
                   │   Atomically Enriched     │
                   │   Customer ZIP & Landing  │
                   │  00_unvibecode_results    │
                   └───────────────────────────┘
```

## Detailed Component Breakdown

### 1. Preflight & Size Estimation (`shipreadyv2.cli` & `shipreadyv2.customer_runner`)
- Filters supported extensions: `.py`, `.js`, `.jsx`, `.mjs`, `.cjs`, `.ts`, `.tsx`, `.rs`, `.go`, `.php`, `.rb`, `.html`, `.htm`, `.css`.
- Ignores runtime and build folders: `.git`, `node_modules`, `venv`, `.venv`, `__pycache__`, `dist`, `build`, etc.
- Token heuristic: `source_bytes / 3.2`. If > 2,000,000 tokens, switches to Fast Lane only (Code Understanding without Business Analysis).

### 2. Fast Lane Engine (`00a_shipreadyv2_fast_lane_v11_api_context_bundle.py`)
- Python AST + Tree-sitter multi-language backend (`tree_sitter_language_pack` / `tree_sitter_languages`).
- Resolves file imports, symbols, and cross-file calls.
- Constructs PyVis interactive network visualization (`01_connected_code_map_for_llm.html`).
- Generates context bundles for LLMs:
  - Narrow (~30K tokens)
  - Optimal (~45K tokens)
  - Wider (~75K tokens)
- Builds initial `complete_repository_context_for_llm.zip` containing `manifest.json`, `chunks.jsonl`, `connections.jsonl`, and `selections.jsonl`.

### 3. Business Analysis Pipeline (Steps 01-06)
- **Step 01 (`01_shipreadyv2_merged_graph_pipeline_5chunks.py`)**: Creates graph-aware LLM batches and 50K-70K semantic packs.
- **Step 02 (`02_shipreadyv2_prepare_pass1_inputs.py`)**: Assembles Pass 1 inputs.
- **Step 03 (`03_shipreadyv2_pass1_full_runner.py`)**: Queries hosted `gpt-5.4-mini` to extract business capabilities, state transitions, actor goals, and activation facts.
- **Step 04 (`04_shipreadyv2_business_path_compiler.py`)**: Compiles raw model outputs into structured workflows; verifies against `normalized_business_path.schema.json`.
- **Step 05 (`05_shipreadyv2_critical_business_insight_selector_v4.py`)**: Deterministic proof obligation evaluation against `universal_insight_rules.yaml`. Gates findings by evidence.
- **Step 06 (`06_shipreadyv2_step4_v2_with_v4_inputs.py`)**: Synthesis via `gpt-5.4` to confirm flaws, generate remediation, and format `03_business_risk_findings.html`.

### 4. Post-Processing & Packaging (`completed_context_export.py` & `redaction.py`)
- Redaction screenings replace detected API keys, passwords, bearer tokens, PEM keys, and credentials with `<REDACTED_*>` markers.
- `enrich_completed_zip` replaces the initial ZIP with an enriched package containing `workflow_context.md`, `workflow_selections.json`, and markdown summaries.
- Customer dashboard is written to `00_unvibecode_results.html`.