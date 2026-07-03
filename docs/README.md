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
`medical-figure-design`, `medical-research-lit`, `medical-statistical-review`,
`medical-table-design`, `medical-submission-prep`, `medical-data-governance`,
and gallery review surfaces support the MAS overlay. The writing/review/figure/literature/statistics/table/submission/data-governance
professional skills are maintained here as a single source for MAS consumption;
stage-prompt routing and generated artifacts remain with their owning runtime or
domain repo.

Current classification: eight active professional modules, all backed by real
syncable Codex specialist skills. Generic source or external-learning intake
belongs to OPL Framework or MAS stage/source surfaces and is not kept here as a
contract placeholder. Omics belongs in this repository only after MAS has a
stable real omics specialist workflow to maintain. Active data governance now
routes to `medical-data-governance`; the legacy Data module remains as
descriptor/readback compatibility.

For literature access, use `medical-research-lit` for the AI workflow and OPL
Connect for stable PubMed refs: `opl connect pubmed search --query <query>
--limit <n> --json`. The connector output should be recorded as
`pubmed_source_refs` and `pubmed_connector_invocation_ref`; MAS keeps citation
judgment, evidence interpretation, owner receipts, typed blockers, and
publication decisions.

The current professional quality floor is in the eight real skills. Figure work
requires a figure contract, evidence chain, candidate loop, and visual QA;
writing requires an argument contract, terminology ledger, paragraph job map,
and citation/availability audits; review requires reviewer lanes and a
cross-review synthesis; literature work requires source routing,
deduplication, support-strength grading, and citation integrity notes;
statistical review requires estimand, denominator, assumption, effect-size,
and action-matrix checks; table design requires table-shell, source-metric,
denominator, footnote, QC, and table-to-claim checks; submission prep requires
journal-instruction, reporting-guideline, declaration, availability,
reviewer-response, and package-consistency checks; data governance requires
clinical data manifests, dictionaries, cleaning/normalization readiness, version
impact review, study binding, privacy/access tier, and lifecycle guardrails.

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
