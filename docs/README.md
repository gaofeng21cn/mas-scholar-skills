# MAS Scholar Skills Docs

Owner: `One Person Lab`
Purpose: `docs_index`
State: `active_index`
Machine boundary: Human-readable navigation. Machine truth remains in
contracts, skill pack files, source, gallery manifests, OPL Framework readback,
and repo-native verification.

`MAS Scholar Skills` is the canonical name for the OPL-owned
`mas-scholar-skills` external enhancement pack. The historical
`opl-scholarskills` name is a compatibility alias. This repo is not a generic
OPL base, not an additional brand module, and not a domain truth owner. Its
docs stay compact: module contracts, quality floors, source packs,
external-learning refs, professional syncable skills
`medical-manuscript-writing`, `medical-manuscript-review`,
`medical-figure-design`, `medical-research-lit`, and gallery review surfaces
support the MAS overlay. The write/review/figure/lit professional skills are maintained
here as a single source for MAS consumption; stage-prompt routing and generated artifacts
remain with their owning runtime or domain repo.

Current classification: ten capability-module contracts, four real syncable
Codex specialist skills, and six contract-layer modules. `tables`, `stats`,
`omics`, `submit`, `data`, and `intake` stay as refs/checklist/candidate-handoff
contracts until a stable active workflow justifies promoting one into a real
skill.

For literature access, use `medical-research-lit` for the AI workflow and OPL
Connect for stable PubMed refs: `opl connect pubmed search --query <query>
--limit <n> --json`. The connector output should be recorded as
`pubmed_source_refs` and `pubmed_connector_invocation_ref`; MAS keeps citation
judgment, evidence interpretation, owner receipts, typed blockers, and
publication decisions.

## Current Docs

| Doc | Role | Boundary |
| --- | --- | --- |
| [Capability modules](./capability-modules.md) | Canonical human-readable module library overview | Machine truth stays in `contracts/scholar-skills-capability-modules.json`, skill pack files, source, and OPL Framework readback |
| [MAS Scholar Skills operating model](./mas-scholar-skills-operating-model.md) | MAS overlay routing, professional-skill single-source policy, pack/default ownership, Connect/Fabric sync, and no-dual-source boundary | MAS ledgers, owner receipts, typed blockers, queues, artifact authority, and publication readiness remain outside this repo |
| [Candidate artifact engines](./candidate-artifact-engines.md) | Candidate artifact body generator boundary and CLI orientation | Candidate artifacts are non-authoritative and require domain owner consumption |
| [Display gallery](./gallery/display-gallery.md) | Human review entry for Scholar Display gallery refs | Pack source and compact review refs live in this repo; consuming MAS/domain owners still own paper truth, visual audit receipts, and publication readiness |

## Growth Rule

Do not create empty OPL-family taxonomy directories for alignment. Add
`active/`, `references/`, `history/`, or other lifecycle directories only when
MAS Scholar Skills gains durable material that cannot stay in this small index.
