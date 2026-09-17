# MAS Scholar Skills Docs

Owner: `One Person Lab`
Purpose: `docs_index`
State: `active_index`
Machine boundary: Human-readable navigation. Package identity, exports, module ids, authority flags, skill bodies, gallery bytes, installed currentness, and consuming-domain decisions remain in contracts, source, manifests, OPL readback, repo-native verification, and MAS/domain owner surfaces.

`mas-scholar-skills` is a consumer-neutral capability Package that MAS and MAG
consume as a required dependency. The
[operating model](./mas-scholar-skills-operating-model.md) owns what the package
is, how a consumer depends on it, and how its layers hand off.

## Where To Read What

| Topic | Owner |
| --- | --- |
| Package role, consumer dependency profiles, layer split, distribution and discovery | [Operating model](./mas-scholar-skills-operating-model.md) |
| Forbidden authority claims and refs-only handoff rules | [No-authority boundary](./no-authority-boundary.md) |
| Module catalog, provider adapters, publication-layout profiles, ref vocabulary | [Capability modules](./capability-modules.md) |
| Remaining evidence gaps | [Active gaps](./active/mas-scholar-skills-ideal-state-gap-plan.md) |
| Display gallery review package | [Display gallery](./gallery/display-gallery.md) |
| Academic figure pattern: adopt/adapt/reject decisions | [Academic figure landing](./academic-figure-skill-landing.md) |
| K-Dense scientific skills intake and OPL Connect routing | [K-Dense intake](./kdense-scientific-agent-skills-intake.md) |
| Medical Display pack source, renderer and fixtures | [Pack README](../packs/medical-display-core/README.md) |

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

## Document Roles

Each document answers one durable reader question, and the table above is the
routing. Add a document or a lifecycle directory only when no existing owner
serves that question; a new document starts with Owner, Purpose, State, and
Machine boundary metadata, like the current set. Completed plans, dated
closeouts, and execution logs stay in Git history, and `docs/active/` holds only
the remaining gaps.
