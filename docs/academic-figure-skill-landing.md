# Academic Figure Skill Learning Landing

Owner: `MAS Scholar Skills Display`
Purpose: land reusable patterns from `TingxiYu/academic-figure-skill` into existing Display owners
State: `landed_refs_only_candidate`
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
| Pack live regression | `medical-display-core` pack source | six golden example inputs and current renderer entrypoint | temporary render outputs, fingerprints, layout/output inspection candidate | pack-local self-check and real golden render where dependencies are available | all selected examples render and inspect, or non-authoritative `execution_issue_candidate` evidence is returned |
| Integration | Display receipt contract, `medical-figure-design`, shared ref template, this document | verified lane changes | provenance fields, routing rules, external-learning record, mainline audit | focused checks, `./scripts/verify.sh`, manifest status, worktree absorption audit | all adopted/adapted items are done or no-code-needed |

## Adoption Decisions

| Pattern | Classification | Landing |
| --- | --- | --- |
| Figure contract, data-question-first selection, archetype, hero panel, candidate/critic loop | `no_code_needed` | already current in `medical-figure-design` and shared quality refs |
| Real artifact inspection with code-vs-render QA separation | `adapt` | executable `medical-display-qc` candidate inspector |
| Physical dimensions, aspect policy, collision checks | `adapt` | `medical-figure-composer` geometry and fit policy |
| Per-panel asset confirmation and explicit degradation reason | `adapt` | extend existing render/panel receipt vocabulary |
| Fixed-input renderer regression | `adapt` | Display Pack-owned live regression, not a quality verdict |
| Reviewer case structure | `watch_only` | persist only evidence-backed MAS visual-audit lessons |
| Fixed scientific signal thresholds; copying a plotting script and only replacing data; Skill-owned dependency installation; journal rules without provenance; parse-only READY claims | `reject` | forbidden by this landing |

## Risk And Verification

- Risk class: `L3 behavior/contract change`
- Verification budget: `standard`
- TDD: selected only for deterministic QC, composition, and live-artifact
  regressions; each stable defect had to fail before its lane fix.
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

## Fresh Evidence Snapshot

The following commands were run from the isolated landing lane on
`2026-07-10`:

- `python3 scripts/verify-display-gallery-pack.py --check`: exit 0; 54 catalog
  templates, 54 OPL template resources, 6 template examples, 6 golden
  templates, 37 gallery visuals, and 5 review files verified.
- `python3 -S skills/medical-display-qc/kernel.py`: exit 0; 17 no-dependency
  checks passed. The default Python passed 30 checks with Pillow, and the
  prepared Python passed 34 checks with Pillow and PyMuPDF.
- `python3 skills/medical-figure-composer/kernel.py`: exit 0; composition
  kernel self-check passed.
- `python3 packs/medical-display-core/src/fenggaolab_org_medical_display_core/live_regression.py`:
  exit 0; six fixed-input adapters, PNG/PDF/SVG/layout/text inspection,
  confirmed-blank rejection, and non-authoritative dependency classification
  passed without running the dependency-heavy live suite.
- The system-Python full live path, which lacks the prepared PDF/plugin
  dependencies, returned `dependency_unavailable=6`, `render_failed=0`, and
  authority false instead of false-passing uninspected outputs.
- Prepared-runtime live check with `PYTHONPATH=/Users/gaofeng/workspace/med-autoscience/src`
  and `/Users/gaofeng/.py-global/bin/python .../live_regression.py --check --json`:
  exit 0; `state=passed`, `passed=6`, `dependency_unavailable=0`,
  `render_failed=0`, `authority=false`, `publication_ready=false`, and
  `temporary_outputs_retained=false`; every required PNG/PDF/SVG/layout/CSV/MD
  export was structurally inspected and confirmed nonblank.
- `./scripts/verify.sh`: exit 0, including the repo-native display contract
  gate, cheap live-regression self-check, all Skill kernels, OPL consumption
  projection currentness, repository consistency, and no-authority checks.

## Learning Landing Audit

Completion below is scoped to the intended repository-local learning surface.
It does not claim MAS owner acceptance, artifact or visual-audit authority,
current-package authority, submission readiness, or publication readiness.

| Item | Pattern | Local owner surface | Target landing | Status | Completion | Fresh evidence | Missing refs | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Existing figure reasoning workflow | Contract-first, data-question-first figure judgment and final-scale QA | `medical-figure-design` and shared professional refs | Existing Skill workflow remains the canonical figure entry | `no_code_needed` | 100% | `./scripts/verify.sh` exit 0 plus current Skill/ref readback | none | Keep consuming through the existing Skill |
| Executable artifact QC | Inspect actual raster/PDF exports and separate deterministic audit from visual review | `medical-display-qc` | Refs-only artifact inspection kernel and routing findings | `done` | 100% | QC kernel: 17 no-dependency, 30 Pillow, and 34 Pillow/PyMuPDF checks; all exit 0 | none | Consume findings as candidates under the domain owner gate |
| Aspect/collision-safe composition | Preserve aspect ratio, expose physical size, reject invalid overlap/geometry | `medical-figure-composer` | `contain`/`crop` composition and fail-closed geometry checks | `done` | 100% | Composer kernel self-check: exit 0 | none | Use compose-only route for existing panels |
| Fixed-input live regression | Render six golden inputs and inspect ephemeral outputs | `medical-display-core` | Pack-owned live engine plus manifest and repo-native gate | `done` | 100% | Prepared runtime: 6 passed, 0 dependency unavailable, 0 render failed; required PNG/PDF/SVG/layout/text blank fixtures rejected; dependency-only path produced no false pass | none | Rerun for any future pixel/layout/currentness claim |
| Panel asset provenance | Distinguish template reuse, reference-guided redraw, and source-free original render | Receipt contract, `medical-figure-design`, shared refs | Four adaptation modes with exact no-source mapping and no invented provenance | `done` | 100% | Display verifier and full repo verification: exit 0 | none | Emit refs-only receipts for owner consumption |
| Rejected unsafe upstream patterns | Reject fixed thresholds, data-path-only script copying, Skill installs, provenance-free journal rules, and parse-only READY | Repo rules, Skill workflow, live self-check, verifier | Explicit prohibitions and evidence-based progress gates | `done` | 100% | Source scan plus live self-check and `./scripts/verify.sh`: exit 0 | none | Keep rejected unless a future owner-approved contract changes the boundary |
