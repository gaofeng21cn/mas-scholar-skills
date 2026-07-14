# MAS Scholar Skills

本仓是 MAS 的专业能力包与发布载体，不持有 study、publication、artifact 或 owner authority。

- package identity、exports 和 MAS 依赖关系以 `contracts/opl_capability_package_manifest.json` 为准。
- capability catalog 以 `contracts/scholar-skills-capability-modules.json` 为准；可执行 Framework surface 归 `one-person-lab`。
- 安装、更新、修复和回滚走统一 `opl packages` lifecycle。
- `gallery/medical-display/` 承载最终人审发布包。

默认验证入口：`scripts/verify.sh`。

<!-- CODEGRAPH_START -->
## CodeGraph

- 本仓库使用本地 `.codegraph/` 索引；该目录不得纳入 Git。
- 定义、调用、影响范围和代码路径等结构检索优先使用 CodeGraph；字面文本检索使用 `rg`。
- 索引缺失或过期时运行 `codegraph init .` 或 `codegraph sync .`。
<!-- CODEGRAPH_END -->
