# MAS Scholar Skills Ideal-State Gap Plan

Owner: `One Person Lab`
Purpose: `single_active_truth_plan`
State: `active_plan`
Machine boundary: Human-readable current-state and next-audit baton. Package identity, exports, module ids, authority flags, gallery bytes, installed-package currentness, and consuming-domain decisions remain in contracts, source, manifests, OPL package readback, repo-native verification, and MAS/domain owner surfaces.

## Ideal-State Reference

The target is an independently released framework capability provider that:

- keeps one aggregate discovery skill and focused `medical-*` specialist skills;
- exposes MAS paper and MAG grant profiles as required Package
  presence/callability edges with refs-only professional handoffs;
- exposes eight professional modules and two pure provider adapter modules;
- returns refs-only candidate material without owning domain truth, artifacts,
  receipts, blockers, runtime state, current-package state, or readiness;
- independently publishes complete bytes to the owner GHCR `latest-stable`,
  leaves physical lifecycle to the actual carrier, and leaves network/runtime
  execution and receipts to their existing platform owners; and
- keeps public narrative, operating model, invariants, catalog, gallery, and
  active work in separate document roles.

The durable human references are
[the operating model](../mas-scholar-skills-operating-model.md),
[the no-authority boundary](../no-authority-boundary.md), and
[the capability catalog](../capability-modules.md). Machine truth wins over
all three.

## Current State Summary

The audited source snapshot has the following structural shape:

| Theme | Current source evidence | Boundary |
| --- | --- | --- |
| Package | `contracts/opl_capability_package_manifest.json` declares consumer-neutral `framework_capability_package` version `0.2.22` | Owner GHCR publication and complete carrier readback remain unproven; Codex Skill projection is not complete installed truth |
| Consumer profiles | Current `.v1` profiles still declare optional/fail-open fields | Target requires Package identity presence and capability callability for MAS/MAG, with local failure only and no version/ABI/lock/payload solving |
| Skill exposure | 35 discoverable `SKILL.md` entries: 11 aggregate/core and 24 router or named-specialty skills | Presence does not select a specialty or grant authority |
| Module catalog | `contracts/scholar-skills-capability-modules.json` declares eight professional modules and two machine adapter modules | The adapters describe or parse bounded requests; OPL Connect owns I/O and receipts |
| Authority | Contract authority flags are false for domain truth, owner receipts, typed blockers, artifact mutation, current-package authority, and publication readiness | MAS or the consuming domain owner remains authoritative |
| Verification | `scripts/verify.sh` defines `fast`, `render`, and `full` lanes | A passing lane is repository evidence only, not live install, render, domain, or publication readiness |

## Current-State vs Ideal-State Gaps

### Functional / Structural Gaps

State: `package_composition_migration_required`

The current optional/fail-open profiles conflict with the accepted required
presence/callability target. The owner contract and consumers need a dual-read
migration before old fields can be removed. The owner GHCR `latest-stable`,
complete carrier readback, and Plugin-only distinction also need fresh terminal
proof. This document change does not implement or prove those surfaces.

### Test / Evidence Gaps

- Owner GHCR `latest-stable` and complete installed/callable bytes are unknown
  until a fresh owner publication and actual-carrier readback exists; version,
  lock, payload, digest, or Release Set output is not ordinary composition
  currentness.
- Any new renderer or gallery-currentness claim requires a fresh `render` or
  `full` lane in an environment with the declared dependencies.
- Paper artifact quality, owner acceptance, submission readiness, and
  publication readiness are outside this repository and cannot be closed by
  docs, contracts, gallery snapshots, or repository tests.

## Next-Round Agent Prompt

Use the following as the next autonomous audit baton:

```text
Objective: Refresh MAS Scholar Skills Active Truth from the current ideal-state
references and live repository surfaces, then govern only evidence-backed open
gaps.

Write scope: README.md, README.zh-CN.md, docs/**, and only the contracts, skills,
pack source, gallery manifests, tests, or scripts required to close a newly
proven gap.

Non-goals: Do not create MAS/domain authority, a package installer, a network
executor, receipts, typed blockers, artifact truth, publication claims, empty
taxonomy docs, retired entrypoints, duplicate facades, or a second capability
catalog.

Live truth inputs: AGENTS.md; contracts/opl_capability_package_manifest.json;
contracts/scholar-skills-capability-modules.json; contracts/capability_map.json;
.codex-plugin/plugin.json; skills/**/SKILL.md; packs/medical-display-core/;
gallery/medical-display manifests; tests; scripts/verify.sh; and fresh OPL
package readback when install/currentness is in scope.

Required actions: Compare each current claim with machine truth; classify any
gap as structural or evidence-only; update the unique owner document for each
theme; remove completed process history from active docs; retire stale links or
surfaces only after replacement-owner and no-active-caller evidence; keep this
plan limited to current progress, open gaps, and the next baton.

Verification commands: scripts/verify.sh fast; scripts/verify.sh full when the
render environment is available; opl-doc-doctor doctor . --format json; run a
repository-relative Markdown link scan; git diff --check.

Completion gate: Every changed claim has a machine or live-readback source;
there is one Active Truth owner; active docs contain no completed execution
ledger; relative links resolve; repo-native verification passes or an exact
dependency/evidence blocker is recorded. Do not infer runtime, domain,
publication, or production readiness.

Foldback target: Put durable operating facts in the operating model, invariant
facts in the no-authority boundary, catalog facts in capability-modules.md,
public value in the root READMEs, and only remaining gaps plus this next baton
in this file. Historical execution traces remain in Git history.
```
