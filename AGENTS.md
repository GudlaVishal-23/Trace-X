# Workspace Memory & Standing Instructions (TRACE-X)

> **Persistent Agent Memory:** This file defines permanent workspace instructions and behavioral rules loaded automatically by Antigravity in `c:\Neura Track`.

---

## 1. Standing Rule: Ponytail Plugin Activation & Prompt Routing

Whenever the user includes triggers such as:
- `"use the ponytail plugin"`
- `"ponytail"`
- `"be lazy"` / `"lazy mode"`
- `"simplest solution"` / `"minimal code"`
- `"yagni"` / `"shortest path"`
- Or complains about bloat, boilerplate, or over-engineering

**The Assistant MUST immediately:**
1. **Activate the Ponytail Plugin & Skill:**
   - Refer to and enforce the `ponytail` skill at `C:\Users\VISHAL GUDLA\.gemini\config\plugins\ponytail\skills\ponytail\SKILL.md`.
   - Adopt the **Senior Developer Ladder** (Default Intensity: **full**):
     - **Rung 1 (YAGNI):** Does this need to exist at all? If speculative, skip it.
     - **Rung 2 (Codebase Reuse):** Reuse utilities, types, and schemas already in `c:\Neura Track`.
     - **Rung 3 (Stdlib First):** Use Python standard library (`difflib`, `math`, `datetime`, `json`, `pathlib`, `typing`, `sqlite3`) before external packages.
     - **Rung 4 (Native Platform):** PostGIS SQL constraints and spatial functions over custom application-layer geometry math; native CSS over extra JS libraries.
     - **Rung 5 (Installed Deps Only):** Rely on already-installed dependencies (OpenCV, PyTorch, FastAPI, Leaflet). Do not add new packages for what a few lines can accomplish.
     - **Rung 6 (One Line):** If it can be one clean line, make it one line.
     - **Rung 7 (Minimal Working Code):** The shortest, cleanest diff that solves the root cause.
2. **Apply High-Impact Prompt Formulations ("Good Prompts"):**
   - Automatically structure code-generation requests and subagent instructions with high-density, constraint-first prompts:
     - `Target: [Exact problem or file]`
     - `Constraint: Apply Ponytail Ladder (Full). Zero unrequested boilerplate, no single-use factories or speculative abstractions.`
     - `Output format: Code first. Then at most 3 short lines: what was skipped, when to add it.`
3. **Concise Output Standard:**
   - No unnecessary essays, architectural bloat, or defensive prose.
   - Code first, then brief summary: `[code] → skipped: [X], add when [Y].`

---

## 2. Complementary Ponytail Tooling Available

| Command / Tool | Purpose | When to Use |
| :--- | :--- | :--- |
| **`ponytail`** | Full senior dev minimalism ladder on coding tasks. | Every coding, refactoring, or feature request when triggered. |
| **`/ponytail-review`** | Code review focused exclusively on cutting over-engineering and bloat. | When reviewing PRs, diffs, or newly written modules. |
| **`/ponytail-audit`** | Whole-repo scan for over-engineering, dead code, and speculative abstractions. | When auditing the project or optimizing technical debt. |
| **`/ponytail-debt`** | Harvests `# ponytail:` debt comments into a ledger to track deferred shortcuts. | To track conscious shortcuts before production release. |
| **`/ponytail-gain`** | Shows ponytail's measured efficiency scoreboard (less code, faster speed). | To report code reduction impact. |
| **`/ponytail-help`** | Quick-reference card for all ponytail modes. | Quick reference. |

---

## 3. TRACE-X Domain Memory

- **No Continuous Video Duplication:** Store structured `VehicleEvent` records in PostGIS, not raw video.
- **Tri-Level Trajectory Classification:** `CONFIRMED`, `PROBABLE`, `CAMERA_GAP`. Never hallucinate missing plates.
- **Physical Feasibility:** Prune any candidate trajectory link where implied speed $> 160 \text{ km/h}$.

---

## 4. Standing Rule: Mandatory Work & Change Log Tracking (CHANGELOG.md)

> **PERMANENT MEMORY DIRECTIVE:** You will NEVER be reminded of this rule again. Follow it unconditionally.

On **every** feature addition, bug fix, architectural refactoring, or file creation:
1. **Always Update [`CHANGELOG.md`](file:///c:/Neura%20Track/CHANGELOG.md):**
   - **What was done:** Clear description of the implemented capability or fix.
   - **Where (Files):** Exact clickable markdown paths to all files created or modified.
   - **Why it was done:** The technical rationale, root cause, or design objective.
2. **Never skip or defer logging:** Every batch of changes must be reflected in `CHANGELOG.md` before concluding the response.

