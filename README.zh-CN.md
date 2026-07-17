<p align="center">
  <img src="assets/branding/mas-scholar-skills-logo.png" alt="MAS Scholar Skills 标志" width="132" />
</p>

<p align="center">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md"><strong>中文</strong></a>
</p>

<h1 align="center">MAS Scholar Skills</h1>

<p align="center"><strong>面向 MAS 的医学科研专业能力包</strong></p>
<p align="center">图表 · 表格 · 统计 · 文献 · 写作 · 审阅 · 投稿 · 数据治理</p>

<!--
Owner: `mas-scholar-skills`
Purpose: `public_repository_entry_zh_cn`
State: `public_entry`
Machine boundary: Human-readable public entry. Package identity, exports, module ids, skill bodies, authority flags, gallery bytes, installed-package currentness, and consuming-domain decisions remain in contracts, source, manifests, OPL package readback, repo-native verification, and MAS/domain owner surfaces.
-->

<p align="center">
  <img src="assets/branding/mas-scholar-skills-overview-v2.png" alt="MAS Scholar Skills 覆盖医学研究全程的专业能力" width="100%" />
</p>

MAS Scholar Skills 为 MAS 提供可复用、面向具体任务的医学论文专业能力。它帮助
Codex 选择合适的专科 Skill，依据明确证据完成工作，形成可检查的候选材料，并把
结果路由回对应的 MAS Stage owner。

本包是 MAS 的必需依赖，但独立发布，因此专业 Skill、质量参考、Display Pack 和
专科目录可以独立演进。历史名称 `opl-scholarskills` 只保留 provenance，不是当前
可发现的 Skill。

## 能力范围

| 模块 | 典型工作 |
| --- | --- |
| Display | 图形设计、风格、组合、导出检查与视觉审阅候选 |
| Tables | 表壳、分母与指标追踪、跨文稿一致性检查 |
| Statistics | 分析方案与结果审阅、假设、区间与可重复性 |
| Literature | 检索策略、来源筛选、引文核验与 claim-support 映射 |
| Writing | 带证据追踪的文稿章节与修订候选 |
| Review | 独立审阅包、缺陷路由与修订优先级 |
| Submission | 期刊要求、文件清单、声明与回复准备 |
| Data Governance | 数据清单、字典、lineage、生命周期、访问与可重复性候选 |

当前源码导出 35 个 Codex 可发现 Skill：11 个 aggregate/core Skill，以及 24 个
router 或具名专科 Skill。专科 Skill 默认可发现，但只在任务确实匹配时选择。机器
目录还包含 scientific search 与 reference verification 两个纯 adapter module；其
网络执行和 receipt 由 OPL Connect 持有。

当前映射见 [Capability Modules](./docs/capability-modules.md)。

对 EHR 或 registry 证据，`registry_signal_validity_pack` 统一折回一个
`ehr_registry_signal_validity_ref`，其唯一专业 producer/owner route 是
`medical-statistical-review`。其他专科 Skill 可以消费该 ref，但不另建并行有效性判断。

## 与 MAS 一起使用

通过统一 package lifecycle 安装 MAS。OPL 会把 MAS Scholar Skills 作为硬依赖解析，
并将 exported Skill 物化到指定 workspace 或 quest：

```bash
opl packages install mas --scope workspace --target-workspace <workspace_root> --json
opl packages install mas --scope quest --target-quest <quest_root> --json
```

安装状态必须从 OPL fresh readback，不能从本 checkout 反推：

```bash
opl packages status --package-id mas --scope workspace --target-workspace <workspace_root> --json
```

单独 clone 本仓不会安装 MAS，也不能证明已安装包 current。

在 MAS 任务中的常规链路是：

```text
MAS Stage 目标与证据
  -> 匹配的 medical-* 专业 Skill
  -> candidate refs、审阅发现或 route-back 建议
  -> MAS/domain owner 接受、拒绝或重新路由
```

aggregate `mas-scholar-skills` Skill 只负责发现和路由；被选中的 `medical-*` Skill
承载具体专业工作。Stage 是否有效、证据阈值和最终接受仍由 MAS Stage prompt 持有。

## Authority 边界

本包只准备候选材料。它不写 study truth 或 artifact body，不签发 owner/reviewer
receipt，不创建 typed blocker，不改变 runtime state，不选择 current package，也不
声明 publication ready。这些判断始终归 MAS 或 consuming domain owner。

稳定规则和机器引用见 [No-Authority Boundary](./docs/no-authority-boundary.md)。

## Medical Display Gallery

[`gallery/medical-display/`](./gallery/medical-display/) 是紧凑的人审参考包，用于模板
选择和 visual-audit 引用。精确成员与指纹归 manifest/snapshot。Gallery 条目是设计
参考，不证明 live renderer、论文质量、owner acceptance 或 publication readiness。

维护和消费边界见 [Display Gallery](./docs/gallery/display-gallery.md)。

## 仓库地图

```text
skills/                         aggregate、core、router 与专科 Skill
contracts/                      package identity、模块目录与边界
references/                     共用质量与 handoff 引用
packs/medical-display-core/     Display 源 pack 与 renderer 验证
gallery/medical-display/        紧凑人审包
docs/                           operating、catalog、boundary 与 Active Truth 文档
scripts/verify.sh               仓库验证入口
```

## 验证

```bash
scripts/verify.sh fast
scripts/verify.sh render
scripts/verify.sh full
```

`fast` 检查 contracts、adapters、仓库一致性和 Skill kernels；`render` 检查 Gallery
与 renderer regression；`full` 运行两者。任何 lane 通过都只证明对应仓库表面，不
代表 runtime、domain、artifact、publication 或 production ready。

## 文档

- [文档索引](./docs/README.md)
- [Active Truth](./docs/active/mas-scholar-skills-ideal-state-gap-plan.md)
- [Operating Model](./docs/mas-scholar-skills-operating-model.md)
- [Capability Modules](./docs/capability-modules.md)
- [No-Authority Boundary](./docs/no-authority-boundary.md)
- [Display Gallery](./docs/gallery/display-gallery.md)
