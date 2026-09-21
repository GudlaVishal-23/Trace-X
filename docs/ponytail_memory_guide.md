# Ponytail Plugin & Workspace Memory Integration Guide

**Workspace:** `c:\Neura Track`  
**Plugin Installed:** `ponytail` (v1.0)  
**Memory System:** Antigravity Workspace Memory (`AGENTS.md` + `.agents/rules/ponytail_rules.md`)  

---

## 1. How the Memory Works

We have established a permanent, persistent workspace memory in your repository so you never have to re-explain Ponytail or your coding preferences.

The memory is active across three interconnected layers:
1. **[AGENTS.md](file:///c:/Neura%20Track/AGENTS.md) (Workspace Root Memory):** Automatically injected into every agent conversation in this workspace. Defines standing rules for triggering the `ponytail` plugin and the 7-rung minimalist ladder.
2. **[.agents/rules/ponytail_rules.md](file:///c:/Neura%20Track/.agents/rules/ponytail_rules.md) (Hierarchical Rules):** `always_on: true` rule enforcing YAGNI, standard library first, zero unrequested boilerplate, and concise code-first outputs.
3. **[.agents/skills/trace-x-engine/SKILL.md](file:///c:/Neura%20Track/.agents/skills/trace-x-engine/SKILL.md) (Domain Skill):** Instructs the agent to prioritize PostGIS native spatial logic and Python standard libraries (`math`, `difflib`, `datetime`) over bloated external dependencies.

---

## 2. Triggering Ponytail Mode

Whenever you include any of these phrases in your prompt, the agent automatically engages Ponytail mode:
- `"use the ponytail plugin"`
- `"ponytail"`
- `"be lazy"` / `"lazy mode"`
- `"simplest solution"` / `"minimal code"`
- `"yagni"` / `"shortest path"`
- Or complain about over-engineering / unnecessary dependencies

---

## 3. High-Impact Prompt Templates ("Good Prompts")

To get the absolute best results when using the Ponytail plugin, use these prompt templates:

### Template 1: Feature Implementation (Minimalist & Fast)
```text
use the ponytail plugin to implement [FEATURE_NAME].
Constraint: Standard library and already-installed packages first.
Zero speculative abstractions or extra classes. Code first.
```
*Example:*
> "Use the ponytail plugin to implement the vehicle speed estimation helper in `backend/app/utils/speed.py`."

### Template 2: Code Review for Bloat & Over-Engineering
```text
/ponytail-review
Review [FILE_PATH] for over-engineering. What can we delete, simplify, or replace with stdlib?
```
*Example:*
> "/ponytail-review `backend/app/services/trajectory/fusion.py`"

### Template 3: Whole-Codebase Bloat Audit
```text
/ponytail-audit
Scan the repo for unnecessary boilerplate, duplicate helpers, and dead flexibility.
```

### Template 4: Tracking Technical Debt & Shortcuts
```text
/ponytail-debt
Show all ponytail debt comments in the codebase and summarize what was deferred.
```

### Template 5: Ultra Mode (YAGNI Extremist)
```text
/ponytail ultra
I need [FEATURE]. Do we even need this, and what is the one-line solution?
```

---

## 4. Good Prompt vs. Weak Prompt Comparison

| Weak Prompt | Good Prompt (Ponytail-Optimized) | Why the Good Prompt Wins |
| :--- | :--- | :--- |
| *"Build an API endpoint for alerts."* | *"Use the ponytail plugin to create `GET /api/alerts`. Use FastAPI with direct SQLAlchemy async query. No repository pattern or factory classes."* | Prevents the model from creating 5 unnecessary abstraction layers (DTOs, factories, unit-of-work classes). |
| *"Help me calculate distance between GPS points."* | *"Use the ponytail plugin: compute Haversine distance in one clean Python function using stdlib `math`. No geopy dependency."* | Avoids installing an unnecessary external dependency (`geopy`) for a 4-line formula. |
| *"Refactor this module."* | *"/ponytail-review on `scripts/simulate_pipeline.py`. Delete dead code and shorten the diff."* | Directly triggers the focused review skill to cut lines of code. |

---

## 5. Summary of Ponytail Slash Commands

- `/ponytail-help` — View all commands and intensity levels (`lite`, `full`, `ultra`).
- `/ponytail-audit` — Whole-repo scan for bloat and over-engineering.
- `/ponytail-review` — Line-by-line review hunting complexity and unnecessary code.
- `/ponytail-debt` — Ledger of conscious `# ponytail:` shortcuts.
- `/ponytail-gain` — Scoreboard of lines of code saved and speed gained.
