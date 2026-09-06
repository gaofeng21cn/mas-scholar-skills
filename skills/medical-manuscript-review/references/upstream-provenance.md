# Upstream Provenance

Read this record when assessing attribution, compatibility or an upstream
refresh. Snapshot checked on 2026-09-06; recheck the actual source before a later
upgrade. Historical learning anchors are retained separately from reviewed heads.

| Source | Historical learning anchor | Reviewed upstream head | License or import status |
| --- | --- | --- | --- |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | `1e024ea8547ada12039edbe8197aaa959d97763f` | `1e5eeffbdad3749125afe7ab48a39694e27f181c` | MIT, Copyright 2025 K-Dense Inc. |
| [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | `c91df241a7a963ea151687ac669c5534404f53e5` | `28150f30f8b4017991fca8c7b2839f02c6586d2f` | Apache-2.0; figure assets may have separate notices. |
| [HughYau/AcademicForge](https://github.com/HughYau/AcademicForge) | `54a2f333973147a1fd703caea6f12252e1f227d6` | `01b6d90c5b50ba0aa48b6564e45ee4a0ade9487c` (`site-first`) | MIT for Forge-owned structure; catalog entries retain their source licenses. |

AcademicForge's reviewed changes affect its hybrid catalog, site and attribution,
not the corresponding specialist methods. Its catalog does not install every
upstream Skill into Scholar. No biology-model runtime change follows from this review.

## Reviewed Method Scope

Reviewed method paths: K-Dense `skills/peer-review/SKILL.md`,
`references/reporting_standards.md` and `skills/scientific-critical-thinking/SKILL.md`;
Nature `nature-reviewer/SKILL.md`, `nature-statistics/SKILL.md`,
`nature-ref-verifier/SKILL.md` and the applicable `nature-shared/core/`
references. Adopt reporting/method distinctions, evidence-linked repairs and
independent review; reject unsupported significance and metadata heuristics.

## Historical OpenScience Source

The local `claimType`, `graphWarnings`, annotation-repair and provenance
patterns refer to [ResearAI/OpenScience](https://github.com/ResearAI/OpenScience)
at historical `f120290c19a79212a1576a1046e64707e9dbb6f0` (short
`f120290`), whose root license was AGPL v3. Its
`resources/skills/ds-science/references/claim-type-discipline.md` distinguishes
computed, parsed, digitized and hypothetical evidence; a digitized value is not
proof of a fresh computation.

Source status is `historical_source_only`. The observed current main
`4ce7d7aad40deb2afd01348f8e3846dba4bb348e` has no common ancestor with that
historical commit. Current README and NOTICE state that public source is no
longer distributed; current LICENSE is the OpenScience Personal and Research
Use License. The public repository carries releases, metadata and licensing.
This review did not inspect a current private implementation or upgrade an
OpenScience runtime. Preserve the independently maintained local patterns;
the historical record is not permission to copy or redistribute current
closed-source software.

## Adoption Boundary

The 2026 update independently restates the task-relevant method decisions in
[method quality reference](method-quality-reference.md). It does not vendor new
upstream scripts, full Skill manuals, model dependencies or assets, or prove
that their current runtimes are installed. Existing Scholar consumer contracts
and accepted project evidence determine the local route.

Upstream review requests for mandatory self-citation, fixed figure/database or
reviewer counts, extra approval stages, automatic delegation, and exclusive
foreign backends are not imported. Scientific claims still need independent
assessment: error-bar overlap alone proves neither no difference nor
equivalence, and a p-value is not the probability that an effect exists.

If a later change copies or adapts substantive upstream text, code or assets,
retain the applicable license, attribution and modification notices, carry the
required resources, and verify that concrete dependency. A learning SHA and an
observed upstream head do not by themselves prove an upgrade or compatibility.
