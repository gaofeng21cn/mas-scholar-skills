<p align="center">
  <img src="assets/branding/mas-scholar-skills-logo.png" alt="MAS Scholar Skills 标志" width="132" />
</p>

<p align="center">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md"><strong>中文</strong></a>
</p>

<h1 align="center">MAS Scholar Skills</h1>

<p align="center"><strong>面向 MAS 医学论文能力的 OPL-owned 外置增强包</strong></p>
<p align="center">图示设计 · 表格整理 · 统计判断 · 文献证据 · 写作修订 · 审阅把关 · 投稿准备 · 数据治理</p>

<!--
Owner: `mas-scholar-skills`
Purpose: `public_repository_entry_zh`
State: `public_entry`
Machine boundary: 人读公开入口。机器真相以 `.codex-plugin/plugin.json`、`skills/mas-scholar-skills/SKILL.md`、`skills/medical-manuscript-writing/SKILL.md`、`skills/medical-manuscript-review/SKILL.md`、`skills/medical-figure-design/SKILL.md`、`skills/medical-research-lit/SKILL.md`、`skills/medical-statistical-review/SKILL.md`、`skills/medical-table-design/SKILL.md`、`skills/medical-submission-prep/SKILL.md`、`skills/medical-data-governance/SKILL.md`、`contracts/domain_descriptor.json`、`contracts/capability_map.json`、`contracts/scholar-skills-capability-modules.json`、gallery manifest/fingerprint、OPL Framework CLI readback 与消费方 domain owner receipt 为准。
-->

<p align="center">
  <img src="assets/branding/mas-scholar-skills-overview.png" alt="MAS Scholar Skills 学术能力流转示意图" width="100%" />
</p>

`MAS Scholar Skills` 是这个仓库和产品的正式名称：一个由 OPL 持有、Codex 可发现、服务 MAS 医学论文能力的外置增强包。历史 `opl-scholarskills` 只保留为兼容别名。本仓是 MAS Scholar Skills 引用、资料包、质量下限、模板、外部学习吸收、模块合同，以及 `medical-manuscript-writing`、`medical-manuscript-review`、`medical-figure-design`、`medical-research-lit`、`medical-statistical-review`、`medical-table-design`、`medical-submission-prep`、`medical-data-governance` 这些可同步专业技能的单源。

MAS 的 stage 主提示词留在 MAS domain-agent 仓：canonical stage source 是 MAS `agent/stages/` 和 `agent/prompts/`。MAS overlay Skill、工作区或 quest 内 `.codex/skills/` 同步副本是 Codex discovery projection / 兼容面，不是 stage authority 的源头；这个同步动作本身必须保留，因为 Codex 依靠 `.codex/skills/` 稳定发现本地技能。`write`、`review`、`figure`、`scout` 等阶段负责什么时候进入、证据够不够、交给谁、怎样 route-back、什么算 owner gate。本仓八个 `medical-*` 技能负责把已经分配下来的写作、审稿、图件、文献、统计、表格、投稿和临床数据治理任务做得更专业。

简单说：MAS Scholar Skills 负责把“可以帮忙做什么、需要什么材料、会交出什么候选结果、最后由谁确认”讲清楚。最终论文真相、成果采纳、质量判断和投稿决策仍然回到对应的领域负责人或智能体。

运行原则是 progress-first 和 AI auto-judgment-first。MAS 不是“AI 只执行、人类才判断”：只要现有证据足够形成候选判断，AI 就应继续给出 AI-consumable evidence、`verdict_candidate`、`route_back_candidate` 和 stop/continue recommendations。只有下一步会越权写入 domain truth、publication readiness、owner receipt、typed blocker，或遇到真实 human gate，才交回 domain owner 或人类。

Display 是其中一个 active 专业模块。MAS Scholar Skills 同时也是 Lit、Tables、Stats、Submit、Write、Review 和 Data Governance 这些学术能力的来源、合同和文档所在地。所有 active 模块共用 refs-only handoff 骨架：`source_pack_ref`、`candidate_package_ref`、`execution_receipt_ref` 和 `owner_gate_handoff_ref`。这些 ref 只描述候选材料和下一跳 owner gate，不创建运行权威或采纳权威。

当前分层固定为：8 个 active 专业模块，全部由真实可同步 Codex 专业 Skill 支撑。active module id 是 `mas-scholar-skills.display`、`mas-scholar-skills.tables`、`mas-scholar-skills.stats`、`mas-scholar-skills.lit`、`mas-scholar-skills.write`、`mas-scholar-skills.review`、`mas-scholar-skills.submit` 和 `mas-scholar-skills.data`；历史 `opl.scholarskills.*` id 只保留为 legacy alias/provenance。`medical-manuscript-writing`、`medical-manuscript-review`、`medical-figure-design`、`medical-research-lit`、`medical-statistical-review`、`medical-table-design`、`medical-submission-prep`、`medical-data-governance` 是 active skill source。通用 source / external-learning intake 归 OPL Framework 或 MAS stage/source surface，不在本仓保留合同占位；组学能力等 MAS 有稳定真实专业 workflow 时，再作为真实专业 Skill 进入本仓。

文献工作现在使用稳定的 OPL Connect PubMed 路径：`medical-research-lit` 负责检索策略、来源筛选、证据地图和 MAS 回流交接；`opl connect pubmed search --query <query> --limit <n> --json` 负责只读 PubMed 访问，并返回 `pubmed_source_refs` 与 `pubmed_connector_invocation_ref`。

当前专业质量地板集中在这八个真 Skill：图件、写作、审阅和文献继续保持 AI-first contract；统计审阅补上 estimand、denominator、assumption、effect-size、multiplicity 和 action matrix；表格设计补上 table shell、source metric、denominator、footnote、QC 和 table-to-claim；投稿准备补上 journal instruction、reporting checklist、declaration、data/code availability、reviewer response 和 package consistency；数据治理补上临床数据 manifest、dictionary/codebook、清洗归一化 readiness、版本影响、study binding、privacy/access 和 lifecycle guardrail。

<table>
  <tr>
    <td width="33%" valign="top">
      <strong>服务对象</strong><br/>
      需要 OPL-owned 增强材料的 MAS overlay 会话与 MAS 医学论文技能
    </td>
    <td width="33%" valign="top">
      <strong>解决问题</strong><br/>
      把 MAS Scholar Skills 引用、资料包、质量下限、外部学习模式和模块合同收成一个单源
    </td>
    <td width="33%" valign="top">
      <strong>交付形态</strong><br/>
      提供候选引用、模板、quality-floor 提示、图表示例和交接包；不替代 MAS owner authority
    </td>
  </tr>
</table>

## 为什么需要 MAS Scholar Skills

学术工作不是一次生成就结束。一个课题通常会反复经历材料接入、数据理解、统计检查、图表设计、文献组织、文字修订、内部审阅和投稿准备。每一步都需要专业判断，能够复用的专业能力应该有稳定单源，而不是散落成临时提示词。

MAS Scholar Skills 的设计目标是把这些可复用支持材料变成 active 专业模块和可同步专家 Skill：

- MAS overlay 和 MAS medical-research skills 可以按同一套语言请求图示、表格、统计、文献、写作、审阅、投稿或数据治理支持。
- 每个模块都说明适合处理什么材料、会产出什么候选结果、需要哪些审阅。
- `medical-manuscript-writing`、`medical-manuscript-review`、`medical-figure-design`、`medical-research-lit`、`medical-statistical-review`、`medical-table-design`、`medical-submission-prep`、`medical-data-governance` 都是本仓真实 Codex Skill，不只是模块 descriptor。
- Source / external-learning intake 归 OPL Framework 或 MAS stage/source surface，不作为本仓 active module 或合同占位；未来组学支持只有在 MAS 形成稳定专业 workflow 后，才作为真实专业 Skill 加入本仓。
- 默认情况下，professional specialist skill 应放在消费它的 domain-agent 仓、贴近 stage 主提示词；只有重型、跨 workspace 复用或需要独立发布/同步时，才拆到外部 pack。本仓就是 MAS 写作、审阅、图件、文献、统计、表格、投稿、Display/source refs 的外部 pack 单源。
- 候选结果可以进入后续人工或领域智能体审阅，但不能自动升级为论文事实。
- 同一个能力包可以同步到不同 MAS 工作区或 quest，而不复制第二套 source of truth。

这种设计让学术能力可以被复用，也让权责边界保持清楚：能力模块负责准备和交接，领域负责人负责采纳和定稿。

MAS Scholar Skills 提到的 `owner_receipt_ref`、`typed_blocker_ref`、`reviewer_receipt_ref`、`route_back_evidence_ref` 或 current-package ref 只是下游 owner-consumption 目标；它们不表示 MAS Scholar Skills 已采纳、已签回执、已创建 blocker，也不授权 publication/current-package readiness。

## Active 专业模块

| 模块 | 用途 |
| --- | --- |
| **学术图示** | 帮助整理图意图、图表结构、视觉模板和人审图库，让研究结果更容易被看懂。 |
| **论文表格** | 为基线表、统计摘要表、结果表和表格质检提供候选结构。 |
| **统计判断** | 帮助组织分析方案、模型选择、可重复性检查和统计结果说明。 |
| **文献证据** | 帮助建立文献地图、引用清单、证据链和已有研究对照。 |
| **写作修订** | 支持摘要、引言、方法、结果、讨论等论文段落的候选草稿与来源追踪。 |
| **审阅把关** | 形成审阅报告、返修建议、route-back 证据和下一步修改入口。 |
| **投稿准备** | 整理投稿包、清单、格式要求和提交前检查材料。 |
| **数据脉络** | 记录数据来源、处理路线、变量说明、血缘关系、存储分层、派生副本盘点、restore-proof retention、已完成项目 closeout、lifecycle catalog 和可复核性线索。 |

这些模块不是独立产品，也不是与 MAS stage 主提示词并列的默认入口。它们是 MAS 可发现和调用的增强能力地图。真正的图表、论文、分析结论、审稿决策和投稿动作，仍由对应的 MAS/domain 系统和负责人确认。

## 外部学习模块映射

ARS、PaperOrchestra、Research-Paper-Writing-Skills、Paperlib、SciPilot Figure、NaturePanelForge、Marsilea 以及科研图示/资源清单里的可迁移做法，只进入 MAS Scholar Skills 的 refs-only 模块映射。落点是八个 active 模块更强的候选引用和检查清单，而不是引入第二套外部 runtime 或 truth source。

专业 Skill 质量地板也吸收 `K-Dense-AI/scientific-agent-skills` 和 `Yuan1z0825/nature-skills` 中可维护的模式：可发现科研技能包、图件契约、先论证后写作、审稿事实基座、来源路由、引用核验、统计诊断、临床表格纪律、数据可用性检查和审稿回复纪律。这些模式会进入 MAS 消费的专业 Skill，而不是作为第二套 runtime 引入。

这些优化优先进度：智能体不需要先安装外部 runtime 才能继续推进。它们增加的是可审阅候选面，例如视觉 QA 预览、引用核查、claim-evidence map、投稿 sanity refs、数据 lineage 和 lifecycle refs；不能绕过 MAS 或其他领域负责人的 owner gate。

## 默认边界防线

新增或争议中的 MAS Scholar Skills 能力，默认按四段拆清楚：

1. **Stage prompt**：MAS `agent/stages/` 和 `agent/prompts/` 负责阶段入口、路由、证据门槛、owner gate、route-back、owner receipt、typed blocker、human gate、publication readiness 和 artifact authority。
2. **Professional specialist skill**：默认归 domain repo；本仓维护可复用外部包里的 `medical-manuscript-writing`、`medical-manuscript-review`、`medical-figure-design`、`medical-research-lit`、`medical-statistical-review`、`medical-table-design`、`medical-submission-prep`、`medical-data-governance` 以及 Display/source refs。这些是实际可同步的 Codex 专家 Skill，不是 descriptor 或脚本函数；它们可以准备 candidate refs 和专业候选产物，但不能采纳它们。
3. **Tool connector**：OPL Connect/Fabric 或其他 connector 只负责工具/API 调用、标准化只读回执、connector error 和资源访问；不负责 stage policy、专业判断、owner receipt、typed blocker、human gate、publication readiness 或 artifact authority。
4. **Contract module**：`contracts/scholar-skills-capability-modules.json` 负责 module id、映射、ref 词汇、无权威标记和同步策略；它不能替代 `medical-*` Skill、stage prompt、connector、owner gate 或 publication-readiness decision。

`mas-scholar-skills` 是本包的聚合入口和 discovery 层；`opl-scholarskills` 只是 legacy alias/provenance entry，不是第二套 truth source。

## 一句话使用方式

你可以直接这样让 Codex 或 OPL 智能体调用它：

- “在 MAS overlay 里以 `medical-figure-design` 为主入口，拉取 MAS Scholar Skills Display refs 形成图件候选包；不要声明 publication readiness。”
- “让 MAS medical-research skills 使用 MAS Scholar Skills Display、Tables、Stats refs，列出下一步最该补的候选材料。”
- “把当前文献证据、写作缺口和投稿准备事项整理成 refs-only MAS 交接清单。”

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

- `MAS Scholar Skills` 是本仓和增强包的正式名称，不是通用 OPL 基座，也不是 MAS/MAG/RCA 的领域真相源。
- 本仓维护可分发的 Codex 插件和技能入口、MAS 消费的医学写作/审阅/图件/文献/统计/表格/投稿/数据治理专业 skill、八模块 active 目录、图库人审包和说明文档。
- OPL Framework 维护可执行命令、同步、运行环境桥接、Connect/Fabric 资源能力和工作台动作。
- MAS overlay 仍是 runtime owner 入口。MAS 在本仓外维护 stage 主提示词，并从本仓消费八个 `medical-*` 专业 skill。
- MAS 等领域智能体继续维护研究事实、论文事实、产物权威、质量裁决、负责人回执、人工门、ledger 和 current package authority。
- MAS Scholar Skills 的输出只能作为候选引用、候选包或审阅提示；不能单独声明运行就绪、领域就绪、质量裁决、产物权威、负责人已接受、可发表或发表就绪（publication readiness）。

<details>
  <summary><strong>给技术操作者看的入口</strong></summary>

### 仓库结构

```text
.codex-plugin/plugin.json              Codex plugin manifest
skills/mas-scholar-skills/SKILL.md     canonical Codex skill entry
skills/medical-manuscript-writing/SKILL.md 医学论文写作专业 skill
skills/medical-manuscript-review/SKILL.md 医学论文审阅专业 skill
skills/medical-figure-design/SKILL.md 医学论文图件设计专业 skill
skills/medical-research-lit/SKILL.md   文献检索专家 Skill
skills/medical-statistical-review/SKILL.md 医学统计审阅专业 Skill
skills/medical-table-design/SKILL.md   医学表格设计专业 Skill
skills/medical-submission-prep/SKILL.md 医学投稿准备专业 Skill
skills/medical-data-governance/SKILL.md 医学数据治理专业 Skill
skills/opl-scholarskills/SKILL.md      legacy alias
contracts/domain_descriptor.json       OMA target descriptor
contracts/capability_map.json          OMA capability target map
contracts/                             module catalog snapshot
gallery/medical-display/               紧凑人审 gallery package
docs/                                  capability 与运维说明
scripts/verify.sh                      仓库验证入口
```

### 同步到工作区或任务

推荐消费面是论文工作区或运行任务内的本地 Codex 发现副本：

```text
<workspace_root>/.codex/skills/mas-scholar-skills/
<workspace_root>/.codex/skills/medical-manuscript-writing/
<workspace_root>/.codex/skills/medical-manuscript-review/
<workspace_root>/.codex/skills/medical-figure-design/
<workspace_root>/.codex/skills/medical-research-lit/
<workspace_root>/.codex/skills/medical-statistical-review/
<workspace_root>/.codex/skills/medical-table-design/
<workspace_root>/.codex/skills/medical-submission-prep/
<workspace_root>/.codex/skills/medical-data-governance/
<quest_root>/.codex/skills/mas-scholar-skills/
<quest_root>/.codex/skills/medical-manuscript-writing/
<quest_root>/.codex/skills/medical-manuscript-review/
<quest_root>/.codex/skills/medical-figure-design/
<quest_root>/.codex/skills/medical-research-lit/
<quest_root>/.codex/skills/medical-statistical-review/
<quest_root>/.codex/skills/medical-table-design/
<quest_root>/.codex/skills/medical-submission-prep/
<quest_root>/.codex/skills/medical-data-governance/
```

使用当前 OPL Framework checkout 的 Connect：

```bash
opl connect sync-skills --domain mas-scholar-skills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain mas-scholar-skills --scope quest --target-quest <quest_root> --json
```

目标目录只应收到技能入口、插件/模块引用与紧凑图库审阅引用。不要把本仓整仓、MAS `outputs/display-pack-gallery/`、渲染缓存、单图导出、依赖锁或图库中间产物复制进每个论文工作区或任务目录。

### 常用读取检查

```bash
opl scholar-skills list --json
opl scholar-skills inspect --module mas-scholar-skills.display --json
opl scholar-skills materialize --module mas-scholar-skills.display --input-ref <ref> --artifact-root <ref-or-path> --output-root <path> --json
opl connect sync-skills --domain mas-scholar-skills --scope codex --json
```

单独克隆本仓不会安装 OPL Framework 的可执行面。需要命令行执行时，应准备当前 `one-person-lab` 检出仓库或发布包。历史 `--domain mas-scholar-skills` 仍作为兼容入口保留。

</details>

## 验证

```bash
scripts/verify.sh
```

验证脚本会检查插件清单、技能入口、模块目录、图库包、无权威边界、忽略中间产物策略和图库产物指纹。

## 继续阅读

- [Capability Modules](./docs/capability-modules.md)
- [MAS Scholar Skills Operating Model](./docs/mas-scholar-skills-operating-model.md)
- [Candidate Artifact Engines](./docs/candidate-artifact-engines.md)
- [Display Gallery](./docs/gallery/display-gallery.md)
- [Gallery Snapshot](./gallery/medical-display/gallery_snapshot.json)
