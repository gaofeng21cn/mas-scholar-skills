# K-Dense Scientific Agent Skills Intake

Owner: `One Person Lab`
Purpose: Record how K-Dense scientific-agent-skills patterns are absorbed into
the eight MAS Scholar Skills real medical specialist skills and routed through
OPL Connect when Codex needs an external scientific Skill.
State: `active_external_learning_intake`
Machine boundary: Human-readable intake note. Machine truth stays in
`contracts/scholar-skills-capability-modules.json`, the eight
`skills/medical-*/SKILL.md` files, `skills/mas-scholar-skills/SKILL.md`, and
repo-native verification.

## Source Inspected

- Source: `/tmp/kdense-scientific-agent-skills`
- Commit: `1e024ea8547ada12039edbe8197aaa959d97763f`
- Relevant skills inspected: `scientific-writing`, `peer-review`,
  `scientific-critical-thinking`, `literature-review`, `paper-lookup`,
  `citation-management`, `scientific-visualization`, `matplotlib`, `seaborn`,
  `statistical-analysis`, `statistical-power`, `experimental-design`,
  `venue-templates`, and `database-lookup`.

## Intake Boundary

Adopt the repeatable contracts, not the foreign runtime. MAS Scholar Skills
keeps K-Dense patterns as refs-only candidate discipline for existing medical
skills. It does not install K-Dense runtimes, make graphical abstracts
mandatory, add default multi-figure quotas, fan out across every database by
default, or create a second owner surface.

MAS or the consuming domain owner still owns domain truth, artifact authority,
owner receipts, typed blockers, current packages, publication readiness, and
final source acceptance.

## Codex Discovery Chain

K-Dense is not only learned background. It is also an approved external Skill
source that Codex may discover through OPL Connect when the default eight
`medical-*` skills do not cover a task-specific capability.

Valid MAS triggers include an explicit user request for a specialist tool or
workflow, a route-back candidate from a default `medical-*` skill, or a MAS
stage prompt identifying a required specialty such as omics, single-cell
analysis, Nextflow, RDKit, PyHealth, or a named scientific database/API.

Use read-only discovery first:

```bash
opl connect external-skills search --query "<scientific need>" --source kdense --json
opl connect external-skills inspect --skill <skill_id> --source kdense --json
```

If the inspected Skill is needed, sync only that one Skill into the active
workspace or quest:

```bash
opl connect external-skills sync --skill <skill_id> --source kdense --scope workspace --target-workspace <workspace_root> --json
opl connect external-skills sync --skill <skill_id> --source kdense --scope quest --target-quest <quest_root> --json
```

The synced Skill remains a refs-only candidate helper. It does not replace the
default MAS Scholar Skills professional package, MAS owner receipts, typed
blockers, current-package authority, artifact authority, domain truth, or
publication readiness.

## Landing Map

| K-Dense pattern | MAS Scholar Skills landing | Local owner surface |
| --- | --- | --- |
| `scientific-writing` two-stage outline to prose, IMRAD, citation style, reporting guidelines | Argument/reader contract, section outline, paragraph job map, final full-prose rule, reporting and citation checks | `medical-manuscript-writing` |
| `peer-review` plus `scientific-critical-thinking` validity, bias, evidence-quality, reproducibility, ethics, and reviewer calibration | Review fact base, validity/bias grid, reviewer lanes, action matrix, venue-calibrated but non-editorial route-back | `medical-manuscript-review` |
| `literature-review`, `paper-lookup`, `citation-management` | Retrieval contract, source routing, multi-source fallback, identifier verification, dedupe, retain/reject/watchlist screening, claim-support matrix | `medical-research-lit` |
| `scientific-visualization`, `matplotlib`, `seaborn` | Plot-selection contract, stable renderer decision, final-size export QA, color/grayscale accessibility, source-data and statistical annotation trace | `medical-figure-design` |
| `statistical-analysis`, `statistical-power`, `experimental-design` | Design unit, estimand, randomization/blocking, power or MDE sensitivity, assumption diagnostics, effect-size/uncertainty, no observed-power shortcut | `medical-statistical-review` |
| Table and statistical display guidance from writing/visualization/statistics skills | Table-vs-figure decision, shell before values, exact metric/denominator trace, no p-value-only evidence, manuscript/figure consistency | `medical-table-design` |
| `venue-templates` and reviewer-response workflow | Current journal instruction contract, article type, file/declaration inventory, graphical abstract only when required, reviewer-response trace | `medical-submission-prep` |
| `database-lookup` retrieval contract | Named authoritative database, accepted identifiers, server/local filter split, pagination/count reconciliation, provenance, untrusted payload handling | `medical-data-governance` |

## Explicit Rejects

- Mandatory graphical abstracts or default figure quotas.
- Treating broad web or database search output as source authority.
- Raw API dumps as a normal handoff format.
- Installing or invoking external runtime skills before candidate refs can move.
- Any MAS Scholar Skills claim of owner acceptance, typed blocker creation,
  publication readiness, current-package authority, or clinical data truth.
