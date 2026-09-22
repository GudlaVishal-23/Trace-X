---
description: Enforces mandatory automatic logging of what was done, where, and why in CHANGELOG.md for all changes.
globs: "**/*"
always_on: true
---

# Standing Rule: Mandatory Work & Change Log Tracking

> **PERMANENT INSTRUCTION:** This rule is automatically loaded on every conversation turn in `c:\Neura Track`.

Whenever any code, file, architecture, or documentation change is made:
1. **Target File:** [`c:\Neura Track\CHANGELOG.md`](file:///c:/Neura%20Track/CHANGELOG.md)
2. **Required Structure per Entry:**
   - **What was done:** Specific capability, fix, or update implemented.
   - **Where (Files):** Exact clickable markdown file links to modified or created files.
   - **Why it was done:** The architectural purpose, problem resolved, or design rationale.
3. **Execution Rule:** This update must happen seamlessly without waiting for the user to prompt or remind the assistant.
