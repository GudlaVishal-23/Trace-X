---
description: Enforces the Ponytail plugin principles (YAGNI, stdlib-first, minimal diffs, senior dev discipline) whenever prompted.
globs: "**/*"
always_on: true
---

# Ponytail Plugin Integration & Prompting Rules

This rule enforces the **Ponytail** engineering philosophy across the `c:\Neura Track` workspace.

## 1. Triggers
This rule and the `ponytail` skill are actively invoked when the user specifies:
- "use the ponytail plugin"
- "ponytail"
- "be lazy" / "lazy mode"
- "simplest solution" / "minimal solution"
- "yagni" / "shortest path"
- "avoid over-engineering" / "no boilerplate"

## 2. Behavioral Directives

When this mode is engaged:
1. **Climb the Ladder:**
   - Check if the task is speculative: Skip it (YAGNI).
   - Check if an existing function/type in `backend/`, `scripts/`, or `data/` already does this: Reuse it.
   - Check if Python standard library does it (`math`, `difflib`, `datetime`, `json`, `collections`): Use stdlib.
   - Check if PostgreSQL / PostGIS handles it natively (`ST_Distance`, constraints, foreign keys): Use DB engine.
   - Check if existing dependencies solve it (PyTorch, OpenCV, FastAPI): Never introduce a new library for a task a few lines can do.
   - If it can be one clean line: Write one line.
   - Only then: Write the absolute minimum code that works.

2. **Zero Unrequested Overhead:**
   - No single-implementation interfaces.
   - No abstract factories for one product.
   - No configuration files for variables that never change.
   - No speculative wrapper classes or premature microservices.

3. **High-Value Prompt Pattern ("Good Prompts"):**
   When delegating or generating code under Ponytail, use the structured pattern:
   ```text
   Task: [Specific feature or fix]
   Mode: Ponytail (Intensity: Full)
   Directives:
   - Root-cause fix over symptom patching.
   - Stdlib and native platform features first.
   - Shortest working diff.
   - Code first, maximum 3-line explanation: what was skipped, when to add it.
   ```

4. **Conscious Shortcut Tagging:**
   If a deliberate simplification is made with a known scale limit, mark it with:
   `# ponytail: [simplification], upgrade to [solution] when [trigger condition]`
