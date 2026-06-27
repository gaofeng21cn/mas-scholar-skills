<p align="center">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md"><strong>中文</strong></a>
</p>

<h1 align="center">OPL ScholarSkills</h1>

<p align="center"><strong>面向 Codex、MAS 与 OPL family agent 的品牌化学术能力 Skill Pack</strong></p>
<p align="center">Display · Tables · Stats · Omics · Literature · Writing · Review · Submission · Data · Intake</p>

<!--
Owner: `opl-scholarskills`
Purpose: `public_repository_entry_zh`
State: `public_entry`
Machine boundary: 人读公开入口。机器真相以 `.codex-plugin/plugin.json`、`skills/opl-scholarskills/SKILL.md`、`contracts/scholar-skills-capability-modules.json`、gallery manifest/fingerprint、OPL Framework CLI readback 与消费方 domain owner receipt 为准。
-->

`OPL ScholarSkills` 把一组聚焦的学术工作能力打包成 Codex-compatible skill pack。本仓是该 skill pack 的 source of truth；MAS 和其他 OPL family agent 通过论文 workspace 或 runtime quest 内的 local Codex discovery path 消费它，同时不把领域 authority 从消费方 agent 搬出来。

每个模块都是 capability descriptor 和 handoff pattern：可以帮助生成 refs-only candidate package、dependency/run-context refs、人审提示和交接材料；不能签 owner receipt、不能改论文 artifact、不能给 quality verdict，也不能声明 publication ready。

<table>
  <tr>
    <td width="33%" valign="top">
      <strong>服务对象</strong><br/>
      需要复用学术能力的 MAS、OPL family agent 与 Codex 会话
    </td>
    <td width="33%" valign="top">
      <strong>提供内容</strong><br/>
      Codex plugin、Skill 入口、十个 module descriptor、authority guardrail 和 display gallery 审阅包
    </td>
    <td width="33%" valign="top">
      <strong>使用方式</strong><br/>
      把紧凑 Skill 同步到 workspace 或 quest-local `.codex/skills/opl-scholarskills`，再由 domain owner 消费、拒绝或 route back candidate refs
    </td>
  </tr>
</table>

## 为什么需要它

研究 agent 需要专业 skill，但专业 skill 不应该变成随机 prompt。ScholarSkills 给这些能力一个共同 OPL 身份、统一 authority boundary 和一致的 handoff contract。

例如 MAS 可以用同一套 module vocabulary 请求 display、table、statistics、writing、review 或 submission 能力。Skill pack 可以准备候选 refs 或人审提示，但 study truth、publication truth、论文 artifact、owner receipt、typed blocker 和 quality verdict 仍归 MAS。

## 核心能力

**十个品牌化学术模块**<br/>
Canonical module catalog 由 [`contracts/scholar-skills-capability-modules.json`](./contracts/scholar-skills-capability-modules.json) 持有，并由 [`skills/opl-scholarskills/SKILL.md`](./skills/opl-scholarskills/SKILL.md) 镜像给 Codex discovery。

**Codex Plugin Packaging**<br/>
本仓通过 `.codex-plugin/plugin.json` 和 `skills/opl-scholarskills/SKILL.md` 直接作为 Codex plugin source。

**Workspace / Quest-local 消费**<br/>
MAS 的默认路径是安装到活跃论文 workspace 或 runtime quest 内的 local Codex discovery path。系统级 Codex 安装和 MAS 程序仓 `plugins/` mirror 是显式开发或历史迁移面，不是默认消费路径。

**默认无 authority**<br/>
所有模块都保持 false authority flags。输出只是 candidate 或 refs，直到消费方 domain owner 接收、拒绝或 route back。

**绘图 Gallery 随 Skill Repo 提供**<br/>
本仓在 [`gallery/medical-display/`](./gallery/medical-display/) 放置紧凑的人审发布包，包括 PDF、manifest、reference、status、quality audit 和 snapshot 元数据。Workspace 和 quest 安装只应暴露这些紧凑 review refs，不复制渲染中间产物。

## 绘图 Gallery

把 gallery 放在 skill repo 里，是因为本仓是 ScholarSkills source of truth，也让运维和审阅更直接：拿到 skill repo 就能打开 `Scholar Display` 的当前人审样例。这里保存的是发布级审阅包，不是 MAS 渲染工作区。

已纳入：

- [`gallery/medical-display/medical_display_gallery.pdf`](./gallery/medical-display/medical_display_gallery.pdf)
- [`gallery/medical-display/gallery_manifest.json`](./gallery/medical-display/gallery_manifest.json)
- [`gallery/medical-display/medical_display_gallery_reference.md`](./gallery/medical-display/medical_display_gallery_reference.md)
- [`gallery/medical-display/display_pack_gallery_status.md`](./gallery/medical-display/display_pack_gallery_status.md)
- [`gallery/medical-display/display_pack_gallery_quality_audit.md`](./gallery/medical-display/display_pack_gallery_quality_audit.md)
- [`gallery/medical-display/gallery_snapshot.json`](./gallery/medical-display/gallery_snapshot.json)

当前 snapshot 字段和 fingerprint 由
[`gallery_manifest.json`](./gallery/medical-display/gallery_manifest.json) 与
[`gallery_snapshot.json`](./gallery/medical-display/gallery_snapshot.json) 持有。
`scripts/verify.sh` 会检查 gallery package，并保持 publication-ready claim 未授权。

不纳入：

- MAS `outputs/display-pack-gallery/`
- 单图 PNG/SVG/HTML 导出
- render cache
- layout sidecar
- dependency lock 或 run-context 文件
- 生成过程中的中间 asset 目录

这些文件仍属于可再生成的 MAS/OPL 运维输出，并由本仓 `.gitignore` 排除。

## 边界

`OPL ScholarSkills` 是 OPL-owned capability library，不是新的 OPL 品牌模块，也不是 MAS domain module。

OPL Framework 持有可执行 CLI 和 runtime bridge，例如：

```bash
opl scholar-skills list --json
opl scholar-skills inspect --module opl.scholarskills.display --json
opl scholar-skills materialize --module opl.scholarskills.display --output-root /tmp/scholarskills-display --json
opl connect sync-skills --domain scholarskills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain scholarskills --scope quest --target-quest <quest_root> --json
```

MAS 或其他消费方 domain agent 持有：

- domain truth
- study/publication truth
- artifact mutation
- owner receipt
- typed blocker
- human gate
- quality verdict
- publication-ready claim

## 仓库结构

```text
.codex-plugin/plugin.json              Codex plugin manifest
skills/opl-scholarskills/SKILL.md      Codex skill entry
contracts/                             module catalog snapshot
gallery/medical-display/               紧凑人审 gallery package
docs/                                  capability 与运维说明
scripts/verify.sh                      仓库验证入口
```

## 安装与同步

本仓继续作为 source of truth。推荐的 MAS 安装面，是活跃论文 workspace 或 runtime quest 内的紧凑 local Codex discovery 副本：

```text
<workspace_root>/.codex/skills/opl-scholarskills/
<quest_root>/.codex/skills/opl-scholarskills/
```

使用当前 OPL Framework checkout 的 Connect：

```bash
opl connect sync-skills --domain scholarskills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain scholarskills --scope quest --target-quest <quest_root> --json
```

目标目录只应收到 local discovery 和 review 所需的 Skill 入口、plugin/module refs 与紧凑 gallery review refs。不要把 source repo 整仓、MAS `outputs/display-pack-gallery/`、render cache、单图导出、dependency lock 或其他 gallery 中间产物复制进每个论文 workspace 或 quest。不要把 MAS 程序仓 `plugins/opl-scholarskills/` mirror 当作推荐 runtime discovery surface。

直接做 Codex plugin 开发时，可以把本仓作为 plugin source，或显式让 OPL Connect 注册：

```bash
opl connect sync-skills --domain scholarskills --scope codex --json
```

单独 clone 本仓不会安装 OPL Framework 的可执行面。需要 CLI 执行时，应准备当前 `one-person-lab` checkout 或 release bundle。

## 验证

```bash
scripts/verify.sh
```

验证脚本会检查 plugin manifest、Skill 入口、module catalog、gallery package、no-authority boundary、忽略中间产物策略和 gallery artifact fingerprint。

## 进一步阅读

- [Capability Modules](./docs/capability-modules.md)
- [Candidate Artifact Engines](./docs/candidate-artifact-engines.md)
- [Display Gallery](./docs/gallery/display-gallery.md)
- [Gallery Snapshot](./gallery/medical-display/gallery_snapshot.json)
