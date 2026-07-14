# MAS Scholar Skills Docs

Owner: `One Person Lab`
Purpose: `docs_index`
State: `active_index`
Machine boundary: Human-readable navigation. Machine truth remains in
contracts, especially `contracts/opl_capability_package_manifest.json`, `contracts/domain_descriptor.json`,
`contracts/capability_map.json`, and
`contracts/scholar-skills-capability-modules.json`. OPL consumes professional
skills through generic descriptor/provenance readback and loads the separately
declared pure reference-provider runtime binding through OPL Connect; skill pack
files, source, gallery manifests, OPL Framework readback, and repo-native
verification remain the corresponding owner surfaces.

`MAS Scholar Skills` is MAS's required `mas-scholar-skills` capability package.
The external repository separates maintenance and releases; it does not make the
capability optional for MAS. The historical `opl-scholarskills` name is
only history/tombstone/provenance and is not an active Codex skill. This repo owns module contracts, source packs,
quality-floor references, compact review refs, and syncable `medical-*`
professional skills. It does not own MAS study truth, artifacts, owner
receipts, typed blockers, current-package authority, or publication readiness.

Use this page as navigation only:

- Module ids, skill classification, optional specialists, retired optional
  mode redirects, and ref families:
  [Capability modules](./capability-modules.md).
- Stage / specialist / connector / contract ownership:
  [MAS Scholar Skills operating model](./mas-scholar-skills-operating-model.md).
- Refs-only handoff and false-authority flags:
  [No-Authority Boundary](./no-authority-boundary.md).
- Academic figure external-learning decisions, landed Display owners, and
  executable evidence:
  [Academic Figure Skill learning landing](./academic-figure-skill-landing.md).

## Verification Lanes

- `scripts/verify.sh` / `scripts/verify.sh fast` runs contracts, repository
  consistency, and all kernel self-checks without starting the R renderer.
- `scripts/verify.sh render` runs the committed gallery checks, live Display
  regression, and registry renderer regression. The registry cases share one R
  process while restoring options, environment, graphics devices, and random
  state after every case.
- `scripts/verify.sh full` is the union used before integration or release.

Both the gallery-pack verifier and repository consistency verifier consume
`scripts/gallery_policy.py`; Gallery import and no-authority rules therefore
have one executable owner instead of two near-duplicate implementations.

Passing any lane remains structural or test evidence only; it does not create
MAS artifact authority, publication readiness, or owner acceptance.

## Current Docs

| Doc | Role | Boundary |
| --- | --- | --- |
| [Capability modules](./capability-modules.md) | Canonical human-readable module library overview | Machine truth stays in `contracts/scholar-skills-capability-modules.json`, skill pack files, source, and OPL Framework readback |
| [No-Authority Boundary](./no-authority-boundary.md) | Shared README/Skill boundary reference for refs-only candidate handoff and owner-route limits | Machine truth stays in `contracts/capability_map.json`, `contracts/scholar-skills-capability-modules.json`, and consuming MAS/domain owner surfaces |
| [MAS Scholar Skills operating model](./mas-scholar-skills-operating-model.md) | MAS overlay routing, professional-skill single-source policy, pack/default ownership, Connect/Fabric sync, and no-dual-source boundary | MAS ledgers, owner receipts, typed blockers, queues, artifact authority, and publication readiness remain outside this repo |
| [Academic Figure Skill learning landing](./academic-figure-skill-landing.md) | Upstream pattern decisions, Display owner mapping, rejected patterns, and repository-local completion evidence | This is a learning audit, not MAS artifact authority, owner acceptance, current-package authority, or publication readiness |
| [K-Dense scientific-agent-skills intake](./kdense-scientific-agent-skills-intake.md) | External learning absorption map for K-Dense scientific writing, review, literature, visualization, statistics, venue, and database retrieval patterns | Patterns land in existing `medical-*` Skills as refs-only candidate discipline, not as external runtime authority |
| [Display gallery](./gallery/display-gallery.md) | Human review entry for Scholar Display gallery refs | Pack source and compact review refs live in this repo; consuming MAS/domain owners still own paper truth, visual audit receipts, and publication readiness |

## Growth Rule

Do not create empty OPL-family taxonomy directories for alignment. Add
`active/`, `references/`, `history/`, or other lifecycle directories only when
MAS Scholar Skills gains durable material that cannot stay in this small index.
