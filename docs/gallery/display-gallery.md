# MAS Scholar Skills Display Gallery

Owner: `One Person Lab`
Purpose: `human_review_entry_for_scholar_display_capability`
State: `active_support`
Machine boundary: 本文是 Scholar Display 的人读审阅入口。Pack source 与 compact gallery review refs 归本 repo 维护；具体论文 artifact、visual audit receipt、owner gate 和 publication readiness 仍归 MAS / consuming domain owner。

## 定位

`opl.scholarskills.display` 以 `packs/medical-display-core/` 作为当前 MAS Scholar Skills-owned source pack，并以 `gallery/medical-display/` 作为 compact human-review package。它的职责是让 MAS 或其他 OPL family agent 在调用 Scholar Display 前，能快速看到默认图件风格、模板覆盖、renderer policy、quality gate 和已知边界。

Gallery 放在 MAS Scholar Skills repo，是因为本 repo 是 skill pack、source pack 和 review refs 的 source of truth；它提供可审阅的 published review package。Workspace 或 quest-local install 只需要复制 compact review refs，不需要也不应该把渲染工作区带进每个论文目录。

Gallery 只能证明有人可审的可视样例和 manifest surface 存在；它不能证明真实论文 figure ready、visual parity 完成、owner accepted、publication ready、current package ready 或 artifact authority。

## Source Pack 边界

`packs/medical-display-core/` 是 Scholar Display 当前承接的通用医学绘图 source pack。它保存模板 descriptor、R/ggplot2 renderer、共享 R helper、pack Python helper、dependency profile 和 canonical template catalog；这些是可版本化的模板源码，不是 gallery 中间产物。

本仓不提交 MAS `outputs/display-pack-gallery/`、render cache、layout sidecar、单图 PNG/SVG/HTML/PDF 预览全集或每篇论文的 current package。`packs/medical-display-core/display_pack.toml` 固定 `authority = false`、`publication_ready = false`、`artifact_authority = false`、`owner_receipt_authority = false` 和 `typed_blocker_authority = false`。MAS 可以把该 pack 作为外部模板/renderer source 消费，但论文局部 figure purpose、claim/data 绑定、visual audit、publication gate 和 owner/human verdict 仍归 MAS。

## 通用科研做图 Quality Floor

本轮外部学习落到 `scholarskills_scientific_figure_quality_floor.v1`，覆盖数据证据图、页面级组合图、graphical abstract 和其他 design-led display work。它要求先有 figure contract、reference selection、style brief、candidate artifact、critic review、final-size inspection、source preservation 和 owner gate refs；AI 执行者仍可自由选择最适合论文局部主张的图型、布局、面板层级、渲染后端和候选数量。本仓只提高质量下限，不限制上限，也不签发质量 verdict。

## Graphical Abstract 口径

当前 gallery 中的 `submission_graphical_abstract` 只应视为 `lower_bound_design_shell_not_reusable_template_authority`。它暴露的问题不是单个 PNG/SVG 细节可以补救，而是把 graphical abstract 当作固定模板复用：真实 graphical abstract 的结构取决于论文主张、证据链、目标期刊、读者路径和参考风格。单个 Python/SVG shell 只能给出下限示例，不能稳定承担跨论文复用。

后续 `Scholar Display` 使用 graphical abstract 时，最小可接受候选链路是：

- `core_claim_and_evidence_chain_ref`
- `figure_contract_ref`
- `reference_selection_ref`
- `style_brief_ref`
- `candidate_artifact_ref`
- `critic_review_ref`
- `final_size_inspection_ref`
- `domain_owner_gate_ref`

AI 执行者可以按论文局部事实自行选择更合适的图型、布局、面板层级、渲染后端和候选数量；本仓只规定质量下限和 refs-only handoff，不限制上限。参考图只能作为 style target 或 reviewer rubric，不能作为数据来源、claim authority、template authority 或 publication-ready 证据。

## 人审入口

当前 repo-local gallery refs：

- `gallery/medical-display/medical_display_gallery.pdf`
- `gallery/medical-display/medical_display_gallery_reference.md`
- `gallery/medical-display/display_pack_gallery_status.md`
- `gallery/medical-display/display_pack_gallery_quality_audit.md`
- `gallery/medical-display/gallery_manifest.json`
- `gallery/medical-display/gallery_snapshot.json`

这些文件构成可安装/可引用的 compact review package。OPL Connect 同步到 `<workspace_root>/.codex/skills/mas-scholar-skills/`、七个 `medical-*` 专业 Skill 目录或 quest-local 对应目录时，可以带上这些 review refs 或指向它们的轻量 manifest，但不应复制整套 gallery 生成目录。

当前 gallery status、template counts、renderer policy、style profile、palette ref、
publication-ready claim flag 和 artifact fingerprints 由
`gallery/medical-display/gallery_manifest.json` 与
`gallery/medical-display/gallery_snapshot.json` 持有，并由 `scripts/verify-display-gallery-pack.py --check` 和 `scripts/verify.sh` 校验。

## Scholar Display 调用边界

MAS Scholar Skills 输出的 `visual_audit_or_gallery_preview_ref` 应指向上述 MAS Scholar Skills-owned compact gallery review package，或由 domain owner 接受的后续 gallery/ref。该 ref 是 review hint，不是 artifact body authority。

Gallery manifest 或 snapshot 里的 `rendered`、`covered`、`lower_bound_passed` 与 owner/receipt 字样只能描述人审 refs 和来源快照状态；它们不是 MAS owner acceptance、publication readiness、typed blocker、current package authority 或 artifact authority。

调用链仍保持：

```text
MAS Scholar Skills internal display module
  -> candidate display refs / execution receipt candidate
  -> MAS owner-consumption readback
  -> MAS owner gate accept / reject / route back
```

只有 MAS owner gate 才能把具体 figure、visual audit receipt、route-back 或 blocker 纳入论文 truth。Scholar Display gallery 不写 MAS domain truth、owner receipt、typed blocker、runtime queue、publication eval、controller decision、current package 或 paper artifact body。

## Review Package 与排除项

本 repo 保留的是最终人审包：

- PDF gallery
- gallery manifest
- snapshot metadata
- reference/status/audit Markdown

安装到 paper workspace 或 runtime quest 时，允许暴露这些 compact review refs，或暴露指向本 repo refs 的 manifest。以下中间产物不得进入每个论文目录或 quest-local skill install：

- MAS `outputs/display-pack-gallery/`
- `medical_display_gallery_assets/`
- 单图 PNG/SVG/HTML/PDF exports
- render cache
- layout sidecar
- dependency lock、dependency receipt 或 run-context 文件
- renderer payload、临时资产目录或 build-only manifests

## 维护命令

常规维护先在本 repo 校验 pack source 与 compact review refs：

```bash
cd /Users/gaofeng/workspace/mas-scholar-skills
python3 scripts/verify-display-gallery-pack.py --check
./scripts/verify.sh
```

如果未来替换 PDF、manifest、status、reference 或 quality audit，只把最终人审包放入 `gallery/medical-display/`，同步 `gallery_snapshot.json` 的 `included_files` sha256，然后重新运行：

```bash
python3 scripts/verify-display-gallery-pack.py --check
./scripts/verify.sh
```

本 repo 不提交 `outputs/display-pack-gallery/`、`medical_display_gallery_assets/`、单图 PNG/SVG/HTML、render cache、layout sidecar、dependency lock 或 run-context。MAS Scholar Skills 文档只能引用最终 refs 和 fresh readback；不要把 gallery 生成 workspace 复制进 consuming workspace。MAS 可以消费这些 refs，但仍独立持有论文局部 figure purpose、claim/data 绑定、visual audit、publication gate 和 owner/human verdict。
