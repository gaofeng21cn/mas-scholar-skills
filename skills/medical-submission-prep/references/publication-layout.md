## Publication Layout Selection

There are exactly two user modes:

1. When a target journal is named, call `select_publication_layout()` and use
   the matching local journal profile as the authoring and export baseline.
2. When no journal is named, use `general-medical-reader.v1`, the neutral
   publication-grade electronic reading profile.

Read the selected profile from
`packs/medical-publication-layouts/publication_layout_catalog.json`. The built-in
catalog covers JAMA Network, NEJM, The Lancet, The BMJ, Nature Medicine,
Diabetes Care, Cardiovascular Diabetology, BMC Medicine, and the shared
Frontiers journal family. Any normalized journal name beginning with
`Frontiers in ...` selects `frontiers-research-article.v1`; similarly named
singular journals such as `Frontier Medicine` do not. These are locally
maintained adaptation profiles, not copied publisher templates. Their stable
authoring rules are usable offline; changing limits, article types, journal
sections, declarations, and portal file rules must be refreshed from the listed
official source before formal submission.

An unknown or stale journal profile never blocks ordinary writing. Continue with
the general reader template and record `journal_profile_pending_official_mapping`
or `local_profile_selected_refresh_pending`. Do not claim that the journal format
is current until the official instruction refresh is consumed.

Every layout selection exposes exactly two core reader PDFs:

- `paper.pdf`: the selected-layout main manuscript.
- `paper_with_supplementary.pdf`: the main manuscript followed by readable
  supplementary material for the user.

The combined PDF is a reading convenience, not automatically a journal upload
artifact. Keep separately addressable supplementary files in the package and do
not create a third reader-edition PDF. Layout profiles are quality floors and
format adapters; they do not replace manuscript, figure, table, statistical, or
reference Skills.

