# MAS Scholar Skills 仓库协作规范

## 适用范围

本文件适用于仓库根目录及其所有子目录；若更深层目录存在 `AGENTS.md`，以更近者为准。

## 定位

- `MAS Scholar Skills` 是 OPL-owned MAS 医学论文能力增强包，不是 MAS/MAG/RCA domain truth owner，也不是额外 OPL 品牌模块。历史 `OPL ScholarSkills` / `opl-scholarskills` 只作为 legacy alias 和 provenance 使用。
- 本仓持有可分发 Codex plugin/skill、十个 ScholarSkills capability module contract、gallery 人审发布包和人读说明。
- OPL Framework 继续持有 `opl scholar-skills *` CLI、Connect 同步、runtime env bridge、App/workbench action 与 framework runtime substrate。
- MAS 等 domain agent 继续持有 study truth、publication truth、quality verdict、artifact authority、owner receipt、typed blocker、human gate 和 current package authority。

## 开发原则

- 修改前先读用户级 `~/.codex/TASTE.md`、相关 contract、Skill、gallery manifest 和 README；事实以源码、contract、manifest、验证脚本和 GitHub readback 为准。
- 保持 no-authority boundary：本仓产物只能作为 refs-only candidate 或 human-review ref，不能声明 domain ready、runtime ready、publication ready、owner accepted 或 artifact authority。
- Gallery 只提交最终人审包：PDF、顶层 manifest、reference/status/audit 文档和 snapshot 元数据。不要提交 MAS 生成过程中的 `outputs/`、单图 PNG/SVG/HTML、render cache、layout sidecar、dependency lock 或中间资产目录。
- 默认验证入口是 `scripts/verify.sh`。
- 发布或 currentness claim 必须绑定到本仓 GitHub remote、commit SHA、gallery artifact fingerprint 和验证输出。

## 文件边界

- `.codex-plugin/plugin.json` 与 `skills/mas-scholar-skills/SKILL.md` 是 canonical Codex plugin/skill 入口；`skills/opl-scholarskills/SKILL.md` 只保留 legacy alias。
- `contracts/scholar-skills-capability-modules.json` 是本仓承载的 module catalog snapshot；OPL Framework 内的 executable contract/CLI 实现仍由 `one-person-lab` 维护。
- `gallery/medical-display/` 只承载最终审阅包，不承载生成工作区。
- `docs/` 只做说明、边界和运维导航，不做第二 truth source。
