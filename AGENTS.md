# MAS Scholar Skills

本仓是医学研究与基金写作的专业能力 Package，不持有 study、grant、publication、artifact 或 owner authority。

- Package identity 和 consumer dependency 以 `contracts/opl_capability_package_manifest.json` 为准；能力目录与输出边界以 `contracts/scholar-skills-capability-modules.json` 和 `contracts/capability_map.json` 为准。
- 本仓只产生方法、审阅和展示候选；不能签发 MAS/MAG owner receipt、写入领域 truth 或声明 publication/submission ready。
- MAS/MAG 的 required edge 由各 consumer 和当前机器合同共同验证；本仓不得自行扩大 consumer readiness 或跨包生命周期 authority。
- `gallery/medical-display/` 承载最终人审发布包；可选子 Skill exposure 不改变整个 Package 的 dependency 身份。
- 默认验证运行 `scripts/verify.sh fast`；按影响补 render 或 full lane。

<!-- CODEGRAPH_START -->
## CodeGraph

- 本仓库使用本地 `.codegraph/` 索引；该目录不得纳入 Git。
- 定义、调用、影响范围和代码路径等结构检索优先使用 CodeGraph；字面文本检索使用 `rg`。
- 索引缺失或过期时运行 `codegraph init .` 或 `codegraph sync .`。
<!-- CODEGRAPH_END -->
