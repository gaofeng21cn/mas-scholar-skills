# Academic Figure Skill Learning Landing

Owner: `MAS Scholar Skills Display`
Purpose: land reusable patterns from `TingxiYu/academic-figure-skill` into existing Display owners
State: `active_landing_plan`
Machine boundary: this document records design, evidence, adoption decisions, and verification. Executable truth remains in the referenced Skill kernels, Display Pack source, receipt contracts, and repo-native verification.

## External Source

- Repository: `https://github.com/TingxiYu/academic-figure-skill`
- Inspected commit: `9c527d1c1462b5c53d95717a682e68c99eda1425`
- Inspected on: `2026-07-10`
- Evidence read: `SKILL.md`, README, figure contract, layout/checklist/journal/revision references, production assets, composer, QA scripts, eval and benchmark scripts.

The upstream repository is a pattern source only. MAS Scholar Skills does not install its runtime, copy its asset tree, inherit its publication claims, or add a duplicate figure Skill.

## Goal

Make the useful parts executable in the current Display family:

1. inspect real raster/PDF artifacts and emit deterministic refs-only QC findings;
2. preserve panel aspect ratio, reject overlapping geometry, and expose physical-size findings before composition;
3. run fixed-input golden-template renders through the Display Pack and inspect the generated outputs;
4. record per-panel template/asset provenance, semantic match, adaptation mode, transform changes, source-data refs, and degradation reasons;
5. keep AI progress-first: warnings remain repair hints, while only unreadable/missing/blank artifacts, invalid geometry, or hard contract failures stop the candidate path.

## Global Constraints

- Reuse `medical-figure-design`, `medical-figure-style`, `medical-figure-composer`, `medical-display-qc`, and `medical-display-core`; do not create another active module or Skill.
- Keep all outputs refs-only and authority false. MAS/domain owners retain artifact mutation, visual-audit receipt, owner receipt, typed blocker, current-package, and publication authority.
- Do not use fixed scientific signal thresholds. Negative and equivocal results are valid evidence.
- Do not mechanically copy a foreign plotting script and replace only its data path.
- Do not install dependencies from a Skill or renderer.
- Do not commit gallery intermediates, single-figure previews, render caches, or layout sidecars.
- Do not turn ordinary warnings into a human gate. Emit the smallest repair route and continue when the candidate remains scientifically and visually defensible.

## Owner Map And Lane Interfaces

| Lane | Owner surface | Inputs | Outputs | Verification | Stop condition |
| --- | --- | --- | --- | --- | --- |
| Artifact QC | `medical-display-qc` kernel and Skill | raster/PDF path, expected dimensions, optional page/panel refs | `programmatic_figure_audit_ref`, `export_integrity_ref`, findings and route-back candidate | kernel red/green self-check plus actual temp artifacts | deterministic inspection works without authority claims |
| Composition geometry | `medical-figure-composer` kernel and Skill | outline, panel paths, explicit fit mode | overlap-safe boxes, contain/crop composition, physical-size/aspect findings | kernel red/green self-check with overlap and non-square panels | no implicit stretch; invalid overlap fails closed |
| Pack live regression | `medical-display-core` pack source | six golden example inputs and current renderer entrypoint | temporary render outputs, fingerprints, layout/output inspection candidate | pack-local self-check and real golden render where dependencies are available | all selected examples render and inspect, or typed dependency evidence is returned |
| Integration | Display receipt contract, `medical-figure-design`, shared ref template, this document | three verified lane commits | provenance fields, routing rules, external-learning record, mainline audit | focused checks, `./scripts/verify.sh`, manifest status, worktree absorption audit | all adopted/adapted items are done or no-code-needed |

## Adoption Decisions

| Pattern | Classification | Landing |
| --- | --- | --- |
| Figure contract, data-question-first selection, archetype, hero panel, candidate/critic loop | `no_code_needed` | already current in `medical-figure-design` and shared quality refs |
| Real artifact inspection with code-vs-render QA separation | `adapt` | executable `medical-display-qc` candidate inspector |
| Physical dimensions, aspect policy, collision checks | `adapt` | `medical-figure-composer` geometry and fit policy |
| Per-panel asset confirmation and explicit degradation reason | `adapt` | extend existing render/panel receipt vocabulary |
| Fixed-input renderer regression | `adapt` | Display Pack-owned live regression, not a quality verdict |
| Reviewer case structure | `watch_only` | persist only evidence-backed MAS visual-audit lessons |
| Fixed signal thresholds, uncited journal rules, skill dependency install, parse-only READY, regex self-scoring | `reject` | forbidden by this landing |

## Risk And Verification

- Risk class: `L3 behavior/contract change`
- Verification budget: `standard`
- TDD: selected only for deterministic QC and composition regressions; each new behavior must fail first in the lane self-check.
- Progress-first gate: ordinary semantic/style/export warnings remain repair
  hints; only missing/unreadable/blank artifacts, invalid geometry,
  unsupported visible claims, or another hard contract failure stop the
  candidate path.
- Required final evidence:
  - focused kernel checks;
  - actual raster/PDF inspection;
  - golden fixed-input pack render/readback when the declared runtime is available;
  - receipt and contract validation;
  - full `./scripts/verify.sh` from final main;
  - `git diff --check`, worktree evidence gates, absorption audit, clean-root readback, and remote SHA after push.

## Learning Landing Audit

This table is updated after all lanes are absorbed.

| Item | Local owner surface | Status | Completion | Fresh evidence | Missing refs | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| Existing figure reasoning workflow | `medical-figure-design` | `no_code_needed` | 100% | final main verification pending | none | verify final main |
| Executable artifact QC | `medical-display-qc` | `not_started` | 0% | pending lane | implementation | land and verify |
| Aspect/collision-safe composition | `medical-figure-composer` | `not_started` | 0% | pending lane | implementation | land and verify |
| Fixed-input live regression | `medical-display-core` | `not_started` | 0% | pending lane | implementation/runtime readback | land and verify |
| Panel asset provenance | receipt contract and figure Skill | `not_started` | 0% | pending integration | contract/Skill changes | land and verify |
| Rejected unsafe upstream patterns | repo rules and verification | `not_started` | 0% | pending final scan | none | verify absence |
