# TASTE

Owner: `gaofeng`
Purpose: 统一 OPL ScholarSkills 仓库维护判断偏好。
State: `active_preference`
Machine boundary: 本文是人读维护偏好；项目事实、接口约束、验收结论和机器真相以 plugin manifest、SKILL.md、contracts、gallery manifest、验证脚本和 GitHub readback 为准。

## 原则

1. **Skill pack 优先**

   本仓优先服务 Codex/OPL/MAS 能直接发现和同步的 skill pack，而不是复制 OPL runtime 或 MAS domain authority。

2. **Refs-only 边界清晰**

   ScholarSkills 输出是候选 refs、candidate package、human review hint 或 gallery preview。任何 domain truth、publication readiness、publication ready claim、owner receipt、typed blocker、quality verdict 和 artifact body authority 都必须回到 domain owner。

3. **Target-First / Substrate-As-Path**

   对 skill pack、gallery package、candidate refs 或 scholar-facing delivery 任务，真实进度按可发现 skill、可审阅 candidate package、human review hint、owner decision、artifact delta 或用户可用结果计算；OPL/MAS runtime、queue、stage、read model、测试、docs、gallery preview 和平台修复只是支持证据。ScholarSkills/OPL 执行基座是首选路径，不是 skill pack 交付的前置条件：基座顺畅时走基座，基座卡住时，前端执行者继续推进合法的 refs-only 交付增量，并把暴露出的基座问题作为 side repair lane 记录或修复。只有继续动作会越权写 domain truth/publication authority surface、缺少必要 source/material、或同一写集 ownership 冲突且无法隔离时，才暂停具体目标动作。repair lane 不能吞掉 skill pack 主线，除非用户目标本身就是平台修复。

4. **Gallery 只提交发布包**

   人审需要能直接打开 PDF 和阅读 manifest/status/audit；运维不需要把全部渲染中间结果纳入 Git。生成输出、缓存、单图导出和 layout sidecar 默认 ignored。

5. **双语入口保持用户可读**

   根 README 采用 OPL family 风格，英文和中文都先说明用途、边界、快速开始、gallery 与验证命令。

6. **最小充分验证**

   文档和 packaging 变更用 `scripts/verify.sh`、artifact fingerprint 和 GitHub readback 证明；不能用测试通过替代 MAS owner acceptance。
