# Track 2 — Developer Adoption & Repeat-Usage Proposal

## 1. Recommended Approach

Introduce **UnvibeCode Differential Guard (`unvibecode diff`)** — an incremental architectural drift engine delivered as a **Sub-Second Git Pre-Push Hook and GitHub Pull Request Review Guard**, paired with a **Visible IDE Status Bar Widget**.

Instead of forcing developers to wait 3–15 minutes for a full repository audit, `unvibecode diff` leverages the cached baseline graph (`shipreadyv2_resolved_graph.json` and `normalized_business_paths.json`) to analyze only staged code modifications in **under 2.5 seconds locally** (via deterministic AST traversal) and triggers asynchronous deep workflow reviews in GitHub PR Actions. It answers the developer's core daily question:
> *"Does my 30-line change alter existing business workflows, sever dependencies, or introduce unvetted entrypoints?"*

---

## 2. Supporting Points

### A. Sub-Second Time-to-Value Embedded into Daily Git Rituals
- **The Core Problem with Developer Adoption**: Developers will not manually run a 3-minute CLI tool every morning. Tools that require deliberate out-of-band invocation suffer severe drop-off after Day 1.
- **The Solution**: Split UnvibeCode into a two-tier execution model:
  1. **Tier 1 (Local Pre-Push Gate — < 2.5 seconds)**: When a developer runs `git commit` or `git push`, the local Fast Lane engine (`00a`) uses Tree-sitter to parse only the 1–3 modified files, intersects modified symbol ranges with the cached workflow graph, and immediately reports if any established business path is touched—with **zero network delay and zero LLM latency**:
     ```text
     🛡️ UnvibeCode Guard [1.8s]
     ✓ Protected Workflows Touched: 1 [JWT Session Verification (auth.py:45)]
     ⚠ Architectural Drift: 0 severed links | 0 unauthenticated entrypoints
     👉 PR Impact Preview: file:///.../unvibecode-diff.html
     ```
  2. **Tier 2 (CI Pull Request Action — Asynchronous Deep Review)**: When the PR is opened, the GitHub Action runs the deeper LLM semantic review in the background where a 60-second CI run is completely standard.

### B. Defeating the "Invisible MCP" Trap via Multi-Surface Brand Recall
- The challenge explicitly warns that MCP integrations can make tools feel invisible, eroding product recall. UnvibeCode Differential Guard solves this by making its intelligence proudly attributed across three daily high-frequency surfaces:
  1. **Branded Pull Request Impact Badges**: Every PR receives an interactive, visually distinct status comment:
     > 🛡️ **Verified by UnvibeCode Business Architecture Guard**  
     > *1 Workflow Impacted: Token Refresh Path (auth.py:45 -> session.py:112)*  
     > `[View Interactive Flow Diff]` · `[UnvibeCode Architecture Stability: 98%]`
     Every peer reviewer, tech lead, and engineering manager sees the UnvibeCode brand daily.
  2. **IDE Status Bar Presence**: A lightweight VS Code / Cursor status bar widget: `UnvibeCode: Protected (0 Drift)`, keeping the brand permanently visible during coding.
  3. **Signed Assistant Citations**: When invoked through MCP or CLI, responses explicitly cite the underlying engine:
     `[Architecture Intelligence verified by UnvibeCode Graph Engine v0.3.15]`.

### C. Team-Driven Repeat Usage via Architecture Drift Budgets
- Just as teams enforce code-coverage thresholds (e.g. Codecov) and lint gates, engineering teams adopt UnvibeCode as their **Architectural Drift Budget**.
- If a junior developer modifies an endpoint that breaks an established Business Path without updating documentation, UnvibeCode flags it before merge.
- This creates an institutional repeat-usage loop: developers return daily because UnvibeCode is the accepted gatekeeper of codebase structural integrity.

---

## 3. Implementation Plan (3 Lines)

1. **Phase 1 (Sub-Second CLI Diff)**: Build `unvibecode diff [--staged | --base main]`, reusing `00a` Tree-sitter parsing against cached `shipreadyv2_resolved_graph.json` to compute symbol deltas and affected workflow intersections in < 2.5s locally.
2. **Phase 2 (1-Command Hook & GitHub Action)**: Ship `python -m unvibecode install-hooks` generating `.git/hooks/pre-push` and publish `@financeflash/unvibecode-action@v1` for automated, branded PR architectural impact comments.
3. **Phase 3 (Validation & Repeat-Usage Testing)**: Deploy to a 200-developer pilot across 15 engineering teams; measure repeat usage via Weekly Active Developers (WAD), hook execution frequency, and PR badge click-through rates.

---

## 4. Measurable Success Metrics

- **Hook Activation Rate**: > 40% of first-time `unvibecode review` users install the pre-push hook within 48 hours.
- **Time-to-Value (TTV)**: Reduced from 180s (full scan) to **< 2.5s** for local pre-push feedback.
- **Weekly Active Developers (WAD)**: Active developers executing ≥ 5 differential checks per week.
- **30-Day Hook Retention**: > 65% of installed pre-push hooks active after 30 days (vs < 10% for full CLI reruns).
- **Viral Expansion Coefficient (K-factor)**: % of PR reviewers who install UnvibeCode on their own repositories after viewing an UnvibeCode PR badge (> 0.25).
