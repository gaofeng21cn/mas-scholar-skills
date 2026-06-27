# OPL ScholarSkills Display Gallery

Owner: `One Person Lab`
Purpose: `human_review_entry_for_scholar_display_capability`
State: `active_support`
Machine boundary: 本文是 Scholar Display 的人读审阅入口。Gallery artifact truth 归 MAS Display Pack；本 repo 只保存最终人审发布包，不保存渲染中间结果，也不授权 publication readiness。

## 定位

`opl.scholarskills.display` 复用 MAS Display Pack 作为当前人审 gallery。它的职责是让 MAS 或其他 OPL family agent 在调用 Scholar Display 前，能快速看到默认图件风格、模板覆盖、renderer policy、quality gate 和已知边界。

Gallery 放在本 ScholarSkills repo，是因为本 repo 是 skill pack 的 source of truth；它提供可审阅的 published review package。Workspace 或 quest-local install 只需要复制 compact review refs，不需要也不应该把 MAS 生成工作区带进每个论文目录。

Gallery 只能证明有人可审的可视样例和 manifest surface 存在；它不能证明真实论文 figure ready、visual parity 完成、owner accepted、publication ready、current package ready 或 artifact authority。

## 人审入口

当前 repo-local gallery refs：

- `gallery/medical-display/medical_display_gallery.pdf`
- `gallery/medical-display/medical_display_gallery_reference.md`
- `gallery/medical-display/display_pack_gallery_status.md`
- `gallery/medical-display/display_pack_gallery_quality_audit.md`
- `gallery/medical-display/gallery_manifest.json`
- `gallery/medical-display/gallery_snapshot.json`

这些文件构成可安装/可引用的 compact review package。OPL Connect 同步到 `<workspace_root>/.codex/skills/opl-scholarskills/` 或 `<quest_root>/.codex/skills/opl-scholarskills/` 时，可以带上这些 review refs 或指向它们的轻量 manifest，但不应复制整套 gallery 生成目录。

当前 gallery status、template counts、renderer policy、style profile、palette ref、
publication-ready claim flag 和 artifact fingerprints 由
`gallery/medical-display/gallery_manifest.json` 与
`gallery/medical-display/gallery_snapshot.json` 持有，并由 `scripts/verify.sh` 校验。

## Scholar Display 调用边界

ScholarSkills 输出的 `visual_audit_or_gallery_preview_ref` 应指向上述 MAS-owned gallery surface 或由 domain owner 接受的后续 gallery/ref。该 ref 是 review hint，不是 artifact body authority。

调用链仍保持：

```text
OPL ScholarSkills display descriptor
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

MAS gallery 资产更新仍在 MAS repo 执行。更新完成后，只把最终审阅包复制回本 repo：

```bash
cd /Users/gaofeng/workspace/med-autoscience
./scripts/run-python-clean.sh scripts/build-display-pack-gallery.py --publish-docs
```

只需要重打包已存在 docs mirror 时：

```bash
cd /Users/gaofeng/workspace/med-autoscience
./scripts/run-python-clean.sh scripts/build-display-pack-gallery.py --publish-docs --package-only
```

本 repo 不提交 `outputs/display-pack-gallery/`、`medical_display_gallery_assets/`、单图 PNG/SVG/HTML、render cache、layout sidecar、dependency lock 或 run-context。OPL ScholarSkills 文档只能引用最终 refs 和 fresh readback；不要把 MAS gallery manifest 当成 OPL-owned truth，也不要把 gallery 生成 workspace 复制进 consuming workspace。
