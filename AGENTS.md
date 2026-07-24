# MAS Scholar Skills

本仓是独立的 `OPL Package` 专业能力包；machine kind 为 `framework_capability_package`，不持有 study、grant、publication、artifact 或 owner authority。

- Package identity、exports 和当前 MAS/MAG consumer profiles 以 `contracts/opl_capability_package_manifest.json` 为机器事实；其中 optional/fail-open 字段是待迁移合同，不是长期组合规则。
- 目标态中 MAS 与 MAG 都把本 Package 作为 required dependency：普通 readiness 只检查 Package identity 存在且所需 capability 可调用；缺失只阻断对应 consumer，不阻断无关 Package，也不引入跨包 version/ABI、lock、payload、digest 或原子闭包。
- Package owner 独立发布完整 bytes 到自己的 GHCR `latest-stable`。Codex Plugin/Skill sync 只是 carrier projection，不是 Package identity、完整 installed truth 或发布 authority。
- capability catalog 以 `contracts/scholar-skills-capability-modules.json` 为准；可执行 Framework surface 归 `one-person-lab`。
- 包内具名专科 Skill 可按任务选择；其可选 exposure 不改变整个 Package 对 MAS/MAG 的 required dependency 边。
- Package release proof、provider/runtime receipt 与 MAS/MAG owner receipt 是不同证据面，互不替代。
- `gallery/medical-display/` 承载最终人审发布包。

默认验证入口：`scripts/verify.sh`。

<!-- CODEGRAPH_START -->
## CodeGraph

- 本仓库使用本地 `.codegraph/` 索引；该目录不得纳入 Git。
- 定义、调用、影响范围和代码路径等结构检索优先使用 CodeGraph；字面文本检索使用 `rg`。
- 索引缺失或过期时运行 `codegraph init .` 或 `codegraph sync .`。
<!-- CODEGRAPH_END -->
