<p align="center">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md"><strong>中文</strong></a>
</p>

<h1 align="center">OPL ScholarSkills</h1>

<p align="center"><strong>面向学术工作的 OPL 能力技能包</strong></p>
<p align="center">图示设计 · 表格整理 · 统计判断 · 组学线索 · 文献证据 · 写作修订 · 审阅把关 · 投稿准备 · 数据脉络 · 材料接入</p>

<!--
Owner: `opl-scholarskills`
Purpose: `public_repository_entry_zh`
State: `public_entry`
Machine boundary: 人读公开入口。机器真相以 `.codex-plugin/plugin.json`、`skills/opl-scholarskills/SKILL.md`、`contracts/scholar-skills-capability-modules.json`、gallery manifest/fingerprint、OPL Framework CLI readback 与消费方 domain owner receipt 为准。
-->

<p align="center">
  <img src="assets/branding/opl-scholarskills-overview.png" alt="OPL ScholarSkills 学术能力流转示意图" width="100%" />
</p>

`OPL ScholarSkills` 把学术工作中常见、可复用的能力整理成一个 Codex 技能包。它不是新的论文系统，也不替研究者或领域智能体做最终判断；它的作用是让 Codex、MAS 和其他 OPL 智能体在需要图表、表格、统计、文献、写作、审阅、投稿和数据整理能力时，有一组稳定、可发现、边界清楚的能力入口。

简单说：ScholarSkills 负责把“可以帮忙做什么、需要什么材料、会交出什么候选结果、最后由谁确认”讲清楚。最终论文真相、成果采纳、质量判断和投稿决策仍然回到对应的领域负责人或智能体。

<table>
  <tr>
    <td width="33%" valign="top">
      <strong>服务对象</strong><br/>
      需要复用学术能力的 Codex 会话、MAS 研究任务，以及 OPL 系列里的其他专业智能体
    </td>
    <td width="33%" valign="top">
      <strong>解决问题</strong><br/>
      把零散的学术辅助能力收成十个清晰模块，方便在不同论文、课题和智能体之间复用
    </td>
    <td width="33%" valign="top">
      <strong>交付形态</strong><br/>
      提供候选引用、审阅提示、材料清单、图表示例和交接包；不直接替代最终论文判断
    </td>
  </tr>
</table>

## 为什么需要 ScholarSkills

学术工作不是一次生成就结束。一个课题通常会反复经历材料接入、数据理解、统计检查、图表设计、文献组织、文字修订、内部审阅和投稿准备。每一步都需要专业判断，但这些判断又不应该散落成临时提示词。

ScholarSkills 的设计目标是把这些能力变成可复用的“能力模块”：

- 研究智能体可以按同一套语言请求图表、表格、统计、文献或写作支持。
- 每个模块都说明适合处理什么材料、会产出什么候选结果、需要哪些审阅。
- 候选结果可以进入后续人工或领域智能体审阅，但不能自动升级为论文事实。
- 同一个能力包可以在不同工作区、不同任务和不同 OPL 智能体之间同步使用。

这种设计让学术能力可以被复用，也让权责边界保持清楚：能力模块负责准备和交接，领域负责人负责采纳和定稿。

## 十个能力模块

| 模块 | 用途 |
| --- | --- |
| **学术图示** | 帮助整理图意图、图表结构、视觉模板和人审图库，让研究结果更容易被看懂。 |
| **论文表格** | 为基线表、统计摘要表、结果表和表格质检提供候选结构。 |
| **统计判断** | 帮助组织分析方案、模型选择、可重复性检查和统计结果说明。 |
| **组学线索** | 面向组学矩阵、特征筛选、通路线索和质量检查，整理可交接的分析候选。 |
| **文献证据** | 帮助建立文献地图、引用清单、证据链和已有研究对照。 |
| **写作修订** | 支持摘要、引言、方法、结果、讨论等论文段落的候选草稿与来源追踪。 |
| **审阅把关** | 形成审阅报告、返修建议、route-back 证据和下一步修改入口。 |
| **投稿准备** | 整理投稿包、清单、格式要求和提交前检查材料。 |
| **数据脉络** | 记录数据来源、处理路线、变量说明、血缘关系和可复核性线索。 |
| **材料接入** | 帮助把新课题、新材料或外部包接入到可治理的研究工作区。 |

这些模块不是十套独立产品，而是一组可以被 OPL / Codex / MAS 发现和调用的学术能力地图。真正的图表、论文、分析结论、审稿决策和投稿动作，仍由对应的领域系统和负责人确认。

## 一句话使用方式

你可以直接这样让 Codex 或 OPL 智能体调用它：

- “用 ScholarSkills 帮这个课题整理一版图表候选包，但不要声明可发表，等 MAS 负责人审阅门确认。”
- “针对这批结果，先用学术图示、论文表格和统计判断三个模块列出下一步最该补的候选材料。”
- “把这篇论文当前的文献证据、写作缺口和投稿准备事项整理成可交接清单。”

## 当前包含的审阅样例

本仓随包提供一个医学图示图库，方便用户和操作者直接查看 Scholar Display 的当前视觉样例。它是人审参考包，不是论文发表授权。

- [`gallery/medical-display/medical_display_gallery.pdf`](./gallery/medical-display/medical_display_gallery.pdf)
- [`gallery/medical-display/medical_display_gallery_reference.md`](./gallery/medical-display/medical_display_gallery_reference.md)
- [`gallery/medical-display/display_pack_gallery_status.md`](./gallery/medical-display/display_pack_gallery_status.md)
- [`gallery/medical-display/display_pack_gallery_quality_audit.md`](./gallery/medical-display/display_pack_gallery_quality_audit.md)
- [`gallery/medical-display/gallery_manifest.json`](./gallery/medical-display/gallery_manifest.json)
- [`gallery/medical-display/gallery_snapshot.json`](./gallery/medical-display/gallery_snapshot.json)

图库只保存最终人审包。渲染中间结果、单图导出、缓存、版式旁路文件和依赖锁不进入本仓。

## 当前边界

- `OPL ScholarSkills` 是 OPL 持有的学术能力技能包，不是 MAS/MAG/RCA 的领域真相源。
- 本仓维护可分发的 Codex 插件和技能入口、十个能力模块目录、图库人审包和说明文档。
- OPL Framework 维护可执行命令、同步、运行环境桥接和工作台动作。
- MAS 等领域智能体继续维护研究事实、论文事实、产物权威、质量裁决、负责人回执、人工门和 current package authority。
- ScholarSkills 的输出只能作为候选引用、候选包或审阅提示；不能单独声明运行就绪、领域就绪、质量裁决、产物权威、负责人已接受、可发表或发表就绪（publication readiness）。

<details>
  <summary><strong>给技术操作者看的入口</strong></summary>

### 仓库结构

```text
.codex-plugin/plugin.json              Codex plugin manifest
skills/opl-scholarskills/SKILL.md      Codex skill entry
contracts/                             module catalog snapshot
gallery/medical-display/               紧凑人审 gallery package
docs/                                  capability 与运维说明
scripts/verify.sh                      仓库验证入口
```

### 同步到工作区或任务

推荐消费面是论文工作区或运行任务内的本地 Codex 发现副本：

```text
<workspace_root>/.codex/skills/opl-scholarskills/
<quest_root>/.codex/skills/opl-scholarskills/
```

使用当前 OPL Framework checkout 的 Connect：

```bash
opl connect sync-skills --domain scholarskills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain scholarskills --scope quest --target-quest <quest_root> --json
```

目标目录只应收到技能入口、插件/模块引用与紧凑图库审阅引用。不要把本仓整仓、MAS `outputs/display-pack-gallery/`、渲染缓存、单图导出、依赖锁或图库中间产物复制进每个论文工作区或任务目录。

### 常用读取检查

```bash
opl scholar-skills list --json
opl scholar-skills inspect --module opl.scholarskills.display --json
opl scholar-skills materialize --module opl.scholarskills.display --input-ref <ref> --artifact-root <ref-or-path> --output-root <path> --json
opl connect sync-skills --domain scholarskills --scope codex --json
```

单独克隆本仓不会安装 OPL Framework 的可执行面。需要命令行执行时，应准备当前 `one-person-lab` 检出仓库或发布包。

</details>

## 验证

```bash
scripts/verify.sh
```

验证脚本会检查插件清单、技能入口、模块目录、图库包、无权威边界、忽略中间产物策略和图库产物指纹。

## 继续阅读

- [Capability Modules](./docs/capability-modules.md)
- [Candidate Artifact Engines](./docs/candidate-artifact-engines.md)
- [Display Gallery](./docs/gallery/display-gallery.md)
- [Gallery Snapshot](./gallery/medical-display/gallery_snapshot.json)
