# 上游来源与同步方式

本文件由三个入口 skill 共享：`sr-gdd`（evidence-to-proposal，出功能 GDD）、`sr-analysis`（media-to-diagnosis，体验诊断）与 `sr-concept`（idea-to-concept，创新功能设计）。上游 skill 本体与模板**不复制、不修改**，以只读方式引用：

- 上游仓库：`<SR_REPO>`（fork 自 DY-2026/GameDesignOS）
- 引用时上游版本：`0855025 Harden v1.3.0.dev0 portability and release readiness`（v1.3.0.dev0）

## 同步上游

```bash
cd <SR_REPO>
git fetch upstream   # 如未配置：git remote add upstream https://github.com/DY-2026/GameDesignOS.git
git merge upstream/main   # 或 rebase，解决冲突后更新本文件的版本记录
```

同步后检查三个入口 skill 引用的上游文件路径是否仍然有效：

- `game-design-proposal-writer/SKILL.md`
- `game-experience-analyzer/SKILL.md`
- `game-experience-analyzer/references/sample-scope-gate.zh-CN.md`
- `game-experience-density-optimizer/`（ED 交接目标）
- `game-concept-architect/SKILL.md`
- `game-concept-architect/references/`（concept-seed-extraction、design-nucleus-options、game-dissection-lens、player-promise-framework、core-loop-expansion、scope-gate、prototype-validation-gate、production-feasibility、genre-fit-matrix、reference-game-boundary，均 `.zh-CN.md`）
- `paranoia-ai-system-evolver/SKILL.md`
- `contracts/decision.schema.json`
- `docs/workflows/evidence-to-proposal.md`
- `docs/workflows/media-to-diagnosis.md`

## 参考样本

- 决议 JSON 格式：以上游 `contracts/decision.schema.json` 为权威定义
- 流程来源：sr-gdd 固化自 `docs/workflows/evidence-to-proposal.md`；sr-analysis 固化自 `docs/workflows/media-to-diagnosis.md`

## 路径约定

本文件与三个 SKILL.md 中使用三个路径变量，由 `team-skills/install.py` 安装时替换为本机实际路径：`<SR_REPO>` 为 GameDesignOS-SR 仓库的本地克隆路径，`<SR_WORKSPACE>` 为团队 workspace 路径，`<SR_PROJECT>` 为 Unity 工程根目录（配表与文本表所在）。手动安装时将三处变量整体替换即可；三个 SKILL.md 与本文件中的所有路径均基于这三个变量书写。

## 已完成波次

- 第一波（2026-07-24）：evidence-to-proposal → `sr-gdd`
- 第二波（2026-07-24）：media-to-diagnosis → `sr-analysis`，产出落 `workspace\analysis\` 与 `workspace\evidence\`
- 第三波（2026-07-24）：idea-to-concept → `sr-concept`（方法论引用 `game-concept-architect`），产出落 `workspace\analysis\`
