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

MAS Scholar Skills 为 MAS 提供可复用、面向具体任务的医学论文专业能力。MAG
消费其中一组更窄但必需的基金能力。两种场景都由
Codex 选择合适的专科 Skill，依据明确证据形成可检查的候选材料，再把结果路由回
consuming domain owner。

本包是 consumer-neutral 的 framework capability provider，并独立发布，因此专业
Skill、质量参考、Display Pack 和专科目录可以独立演进。owner 将完整 Package bytes
独立发布到自己的 GHCR `latest-stable`；Codex Plugin/Skill materialization 只是
carrier projection。目标 MAS/MAG 依赖边只要求 Package identity 存在且必需能力可调用，
不做跨包 version/ABI 求解，也不以 lock、payload、digest、Release Set 或原子闭包为门。
当前 manifest 仍把两个 profile 写成 optional/fail-open；这是待迁移机器事实，不是长期
组合规则。历史名称 `opl-scholarskills` 只保留 provenance，不是当前可发现的 Skill。

## 能力范围

| 模块 | 典型工作 |
| --- | --- |
| Display | 图形设计、风格、组合、导出检查与视觉审阅候选 |
| Tables | 表壳、分母与指标追踪、跨文稿一致性检查 |
| Statistics | 分析方案与结果审阅、假设、区间与可重复性 |
| Literature | 检索策略、来源筛选、引文核验与 claim-support 映射 |
| Writing | 带证据追踪的文稿章节与修订候选 |
| Review | 独立审阅包、缺陷路由与修订优先级 |
| Submission | 离线期刊版式 profile、默认阅读版、文件清单、声明与回复准备 |
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

MAS 必需依赖本 Package，包内具名专科 Skill 仍按任务选择。安装 MAS 时必须确保
ScholarSkills Package identity 和 MAS 必需能力集合存在且可调用；缺失只阻断 MAS 并
进入托管安装/修复，不阻断无关 Package，也不引入 version/ABI/lock/payload 门。
当前 `bundled_capability_package_ids` 与 optional/fail-open profile 字段在迁移期仍作
兼容输入：

```bash
opl packages install mas --scope workspace --target-workspace <workspace_root> --json
opl packages install mas --scope quest --target-quest <quest_root> --json
```

bundled 状态必须从 MAS package surface fresh readback，不能从本 checkout 反推：

```bash
opl packages status --package-id mas --scope workspace --target-workspace <workspace_root> --json
```

单独 clone 本仓不会安装 MAS，也不能证明完整 ScholarSkills bytes 已安装；只有 Codex
Skill projection 同样不够。缺少 required Package identity 或 capability callability
时 MAS fail closed，但无关 Package 继续可用。

在 MAS 任务中的常规链路是：

```text
MAS Stage 目标与证据
  -> 匹配的 medical-* 专业 Skill
  -> candidate refs、审阅发现或 route-back 建议
  -> MAS/domain owner 接受、拒绝或重新路由
```

aggregate `mas-scholar-skills` Skill 只负责发现和路由；被选中的 `medical-*` Skill
承载具体专业工作。Stage 是否有效、证据阈值和最终接受仍由 MAS Stage prompt 持有。

## 与 MAG 一起使用

MAG 原生 grant workflow 始终是唯一的 Stage 与 authority owner。其 required
ScholarSkills capability set 包含 `medical-research-lit`、
`medical-statistical-review`、`medical-methodology-planner`、
`medical-evidence-integrity-reviewer`、
`medical-evidence-synthesis-and-claim-map` 或
`medical-reference-integrity-auditor`。

```text
MAG grant prompt
  -> required ScholarSkills Package 与可调用的基金能力集合
  -> 按任务选择匹配的 medical-* Skill
  -> refs-only candidate handoff
  -> MAG 通过自己的 authority surface 接受、拒绝或 route back
```

缺少 Package identity 或 required capability callability 时只阻断 MAG，并进入托管
安装/修复；不阻断无关 Package，也不把领域 authority 交给 ScholarSkills。具名专科
Skill 的 exposure 仍按任务选择。当前 optional/fail-open machine profile 只作为待迁移
输入，直到 owner contracts 与 consumers 完成更新。

`medical-submission-prep` 内置 offline-first 出版版式目录。指定期刊时选择对应的本地
适配 profile；未指定期刊时使用出版级 `general-medical-reader.v1`。核心阅读输出固定为
`paper.pdf` 和 `paper_with_supplementary.pdf`。正式投稿前必须刷新 profile 链接的官方
要求，才能声称期刊格式符合当前规则。Frontiers 以内置出版社家族 profile 表达，
任意 `Frontiers in ...` 期刊在普通写作时都可离线复用同一维护基线。

## Authority 边界

本包只准备候选材料。它不写 study/grant truth 或 artifact body，不签发
owner/reviewer receipt，不创建 typed blocker，不改变 runtime state 或 strategy
memory，不选择 current package，也不声明 fundability、quality/export 或
publication ready。这些判断始终归 MAS、MAG 或 consuming domain owner。

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
