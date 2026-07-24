# MAS Scholar Skills Docs

Owner: `One Person Lab`
Purpose: `docs_index`
State: `active_index`
Machine boundary: Human-readable navigation. Package identity, exports, module ids, authority flags, skill bodies, gallery bytes, installed currentness, and consuming-domain decisions remain in contracts, source, manifests, OPL readback, repo-native verification, and MAS/domain owner surfaces.

MAS Scholar Skills is a consumer-neutral framework capability provider with
required Package profiles with refs-only handoffs for MAS medical-paper and MAG medical-grant work. It
owns reusable specialist playbooks, refs, packs, module contracts, and compact
gallery review material. It does not own study or grant truth, artifacts, owner
receipts, typed blockers, current-package state, strategy memory, runtime state,
fundability, quality/export verdicts, or publication readiness.

## Active Truth

[MAS Scholar Skills Ideal-State Gap Plan](./active/mas-scholar-skills-ideal-state-gap-plan.md)
is the single owner for current completion, open gaps, evidence limits, and the
next-round Agent prompt. Completed implementation traces belong in Git history,
not in `docs/active/`.

## Canonical Role Map

This compact capability-pack repository maps OPL documentation roles onto
existing owners instead of creating empty parallel files:

| OPL role | Current owner | What it owns |
| --- | --- | --- |
| Project and architecture | [Operating model](./mas-scholar-skills-operating-model.md) | Product role, stage/skill/provider/owner split, package distribution, and discovery path |
| Invariants | [No-Authority Boundary](./no-authority-boundary.md) | Refs-only handoff and forbidden authority claims |
| Capability catalog | [Capability modules](./capability-modules.md) | Human-readable module and skill mapping; machine truth remains in contracts |
| Active progress and gaps | [Active Truth](./active/mas-scholar-skills-ideal-state-gap-plan.md) | Current audited shape, remaining evidence gaps, and next baton |
| Gallery | [Display gallery](./gallery/display-gallery.md) | Compact human-review package boundary and maintenance route |

Separate `docs/project.md`, `docs/status.md`, `docs/architecture.md`, and
`docs/invariants.md` files are intentionally not created while the owners above
remain unambiguous. The doctor warning for those conventional paths is therefore
a profile-shape signal, not missing repository truth.

## Supporting References

- [Academic Figure Skill learning landing](./academic-figure-skill-landing.md):
  stable adopt/adapt/reject decisions and their current owner surfaces.
- [K-Dense scientific-agent-skills intake](./kdense-scientific-agent-skills-intake.md):
  external-learning routing into existing professional skills and OPL Connect.
- [Medical Display Pack README](../packs/medical-display-core/README.md): pack-local
  source, renderer, and verification owner.

## Verification

```bash
scripts/verify.sh fast
scripts/verify.sh render
scripts/verify.sh full
```

- `fast` checks contracts, repository consistency, adapters, and skill kernels.
- `render` checks the committed gallery and live renderer regressions.
- `full` runs both lanes and is the integration/release verification entry.

Passing a lane proves only the tested repository surface. It does not prove an
installed package is current, a renderer is available elsewhere, or a paper is
accepted, submission-ready, publication-ready, or production-ready.

## Growth Rule

`docs/active/` exists only for the durable Active Truth baton. Add lifecycle
directories or new long-lived docs only when a unique role cannot be served by
an existing owner. Every new document needs Owner, Purpose, State, and Machine
boundary metadata; dated closeouts and completed specs remain in Git history.
