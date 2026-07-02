---
name: opl-scholarskills
description: "Legacy compatibility alias for MAS Scholar Skills. Use only when an existing workspace still references opl-scholarskills; for new MAS medical-paper work prefer mas-scholar-skills plus the real skill sources medical-research-write, medical-research-review, medical-research-figure, and medical-research-lit."
---

# OPL ScholarSkills Legacy Alias

This is a compatibility entry for existing local Codex installs that still reference `opl-scholarskills`.

For new work, use:

- `mas-scholar-skills` for the aggregate MAS Scholar Skills capability map.
- `medical-research-write` for medical manuscript writing and revision.
- `medical-research-review` for adversarial medical review and route-back.
- `medical-research-figure` for medical manuscript figures.
- `medical-research-lit` for PubMed-oriented literature discovery.

Do not treat this alias as a separate source of truth. The canonical repository and plugin name is `mas-scholar-skills`; the write/review/figure/lit skill bodies are maintained there and synced for MAS consumption.
