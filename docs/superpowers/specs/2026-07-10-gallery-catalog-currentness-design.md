# Medical Display Gallery Catalog Currentness Design

Owner: `MAS Scholar Skills Display`
State: `implemented_verified`
Machine boundary: 本文记录 compact Gallery 刷新的设计决策；模板、renderer 与数量真相仍归 `packs/medical-display-core/`、Gallery manifest/snapshot 和 repo-native verification，论文 artifact、owner receipt 与 publication readiness 仍归 MAS / consuming domain owner。

## 目标

让 `gallery/medical-display/` 正确投影当前 canonical catalog，同时保持 compact human-review package 边界：

- canonical templates: `54`
- R/ggplot2 templates: `44`，其中 evidence `43`、reporting flow `1`
- Python design templates: `1`
- non-visual table shells: `9`
- Gallery table preview: 仅 `table1_baseline_characteristics`，共 `1`
- Gallery visual total: `46`

## 生成与同步

使用 MAS 既有 `scripts/build-display-pack-gallery.py` 读取 MAS Scholar Skills-owned source pack，生成 HTML、PDF、manifest、reference、status 和 quality audit。重渲染完成后只把以下最终审阅文件同步回本仓：

- `medical_display_gallery.pdf`
- `gallery_manifest.json`
- `medical_display_gallery_reference.md`
- `display_pack_gallery_status.md`
- `display_pack_gallery_quality_audit.md`
- `gallery_snapshot.json`

不提交 `outputs/display-pack-gallery/`、单图 PNG/SVG/PDF、HTML、payload、render cache、layout sidecar、dependency receipt 或 run-context。

Builder 必须执行 template descriptor 声明的 subprocess entrypoint，不假设模板目录存在 legacy `render.R` wrapper。每个 current Gallery evidence template 必须同时具备已注册的 pack-level renderer 和 purpose-specific synthetic Gallery payload；generic synthetic fallback 不能作为 current Gallery card 的最终输入。

## Currentness 与质量门

Gallery manifest 必须由生成器产生，并准确记录 54 个 current canonical templates、43 个 evidence cards、1 个 reporting-flow card、1 个 design card、1 个 table-preview card 和 9 个 non-visual canonical templates。`gallery_snapshot.json` 对最终五个生成文件记录新 SHA-256，并继续声明 refs-only / no-authority 边界。

完成验证包括：

1. focused Gallery verifier 与仓库默认 `scripts/verify.sh` 通过；
2. PDF 页面可由 Poppler 完整渲染，页数、尺寸和非空像素正常；
3. contact sheet 人工检查无空白页、裁切、重叠、黑块或不可读标签；
4. 仓库 diff 可包含必要的 repo-owned renderer、fixture、tests 与 parity gate 变更；`gallery/medical-display/` 本身仍只允许六个最终审阅文件，不得包含任何生成中间物。

Gallery 更新只证明 catalog 投影和人审参考包 current；不证明具体论文 figure ready、owner accepted 或 publication ready。

## 实施证据

- Generator source: MedAutoScience `72b4a2cc` uses the pack-owned registry Gallery fixture as the single payload source.
- Pack source: renderer follow-up `2933cdf` + `aefb859` adds the fixture, specialist registry renderer module, ggconsort cohort-flow dispatch, fail-closed numeric/unit validation, and null-device protection.
- Full force-render: `54` current canonical templates, `46/46` rendered Gallery visuals, `43` evidence figures, `1` reporting flow, `1` design figure, `1` table preview, `9` non-visual table shells, and `0` blocked Gallery visuals.
- Runtime evidence: prepared run-context fingerprint `sha256:68741db24d0dc6f1b17b78e8228dae88bbd29755b062f082179d7270db521764`; pack file SHA inventory was identical before and after rendering, and no `Rplots.pdf` was created.
- Final PDF: `24` A4 pages, SHA-256 `8b038e50ccc9925d97e753919809e35a8a7e52b21d3c00cd5062d3c4a60cec0f`; Poppler rendered all pages, programmatic blank-page inspection found none, and contact-sheet plus focused page review found no clipping, overlap, black blocks, or unreadable labels.
- Repo gate: `python3 scripts/verify-display-gallery-pack.py --check` reports `54` catalog templates, `46` Gallery visuals, and `5` hashed review files. Full `./scripts/verify.sh` remains the final post-write gate.
