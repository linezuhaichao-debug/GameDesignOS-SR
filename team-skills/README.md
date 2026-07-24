# SR 团队工作流 skill

本目录是团队内部的两个工作流 skill，方法论只读引用本仓库的上游 skill（`game-experience-analyzer`、`game-design-proposal-writer`、`paranoia-ai-system-evolver` 等），本目录只固化 SR 团队的项目语境、VOI 门、产出路径与 Human Gate。

| skill | 用途 | 什么时候用 |
| --- | --- | --- |
| `sr_analysis` | 体验诊断 + 设计拆解复刻：先把录屏/截图/PV/商店页等素材分析成证据链报告；你判定"可参考"后再拆成复刻规格，交接给 sr_gdd | "分析这段录屏"、"拆一下这个竞品玩法"、"这个功能能不能复刻" |
| `sr_gdd` | 功能 GDD 工作流：把体验记录、旧策划案、脑图、配置表等材料写成实现粒度的功能 GDD（功能规则、配置契约、验收标准、交接清单） | "写策划案"、"出 GDD"、"把这个整理成功能文档" |

两个 skill 共享 `shared/` 下的项目语境（`sr_project_context.md`：数值铁律、写作约束）与上游说明（`SR_UPSTREAM.md`），安装时必须三个目录一起装。

## 一、安装（团队成员）

前置：已 `git clone` 本仓库，本机有 Python 3。

```bash
cd <仓库路径>
python team-skills/install.py
```

脚本会做三件事：

1. 自动识别仓库路径（`<SR_REPO>`）；
2. 询问 workspace 路径（`<SR_WORKSPACE>`，策划案/证据/决议的落盘位置，通常自动检测正确，回车确认即可）；
3. 询问安装目标目录后，把 `sr_gdd`、`sr_analysis`、`shared` 复制过去，并把文件里的路径变量替换成本机实际路径。

非交互安装（脚本/CI 用）：

```bash
python team-skills/install.py --workspace "D:\GameDesignOS\workspace" --target "D:\.claude\skills" --yes
```

**用的不是 Claude Code？** SKILL.md 是标准 Agent Skills 格式，任何支持该格式的工具都能加载——把 `--target` 指到对应工具的 skill 目录即可（例如 Codex 用 `~/.codex/skills`）。工具完全不支持 skill 格式时，也可以手动复制 `sr_gdd/`、`sr_analysis/`、`shared/` 三个目录到任意位置，把文件里的 `<SR_REPO>`、`<SR_WORKSPACE>` 全局替换为本机路径，然后把 SKILL.md 内容作为提示词使用。

**更新**：`git pull` 后重跑一次 `install.py` 即可（会覆盖旧安装）。

## 二、使用教学

### sr_analysis：分析素材

```
/sr_analysis D:\recordings\新手期首战.mp4
```

或直接说人话："分析一下这段新手期录屏的前期体验"。裸 `/sr_analysis`（不带素材）不会自动开始，会先问你要素材路径和分析目标。

流程上它会先和你确认"这次分析要改变什么决策"（VOI 门），再声明样本能证明什么、不能证明什么，然后产出**证据链报告**（体验报告 + 问题卡）。做完即停，由你在报告门做选择：

| 选项 | 含义 |
| --- | --- |
| `accept_diagnosis` | 接受诊断结论，结束 |
| `enter_dissection` | 判定该功能可参考，进入设计拆解，产出复刻规格 |
| `request_more_evidence` | 证据不足，补素材再来 |
| `route_to_ed_experiment` | 转交给体验密度优化实验 |
| `revise_player_promise` | 回头修订玩家承诺 |
| `stop` | 终止 |

只有选 `enter_dissection` 才会进入第二阶段拆复刻规格；规格会和你迭代到认可后，交接门选 `route_to_sr_gdd` 自动生成给 sr_gdd 的交接材料。

### sr_gdd：出功能 GDD

```
/sr_gdd 基于 英雄改造v0.2.xlsx 出功能 GDD
```

裸 `/sr_gdd` 会先问你要主题和上游材料。**没有任何一份材料是硬性必须的**，最低输入是主题 + 一段能支撑规则粒度的描述；但"旧案（或同等详细度描述）+ 涉及配置表"齐备时效率最高。材料薄不阻塞——会触发决议问答，把关键取舍列成清单请你逐条拍板，它**不替你做设计取舍**。

成稿后的 Human Gate 选项：

| 选项 | 含义 |
| --- | --- |
| `approve` | 批准，决策记录落盘为 accepted |
| `approve_with_conditions` | 有条件批准（条件写进备注） |
| `request_missing_evidence` | 缺上游材料，先补 |
| `revise` | 打回修改 |
| `reject` | 否决 |

### 典型流水线

```
竞品录屏/截图 ──► /sr_analysis ──► 证据链报告 ──(enter_dissection)──► 复刻规格
                                                              │
                                              (route_to_sr_gdd)│
                                                              ▼
旧策划案/配置表 ────────────────────────────────► /sr_gdd ──► 功能 GDD ──► 开发排期
```

### 产出落盘位置

所有产出写入 `<SR_WORKSPACE>` 下（安装时确定）：

| 产出 | 子目录 |
| --- | --- |
| 功能 GDD | `proposals\` |
| 体验报告 / 问题卡 / 复刻规格 / 交接 JSON | `analysis\` |
| 证据包（证据索引、时间戳账本） | `evidence\` |
| 决策记录（decision.schema.json） | `decisions\` |

## 三、数值铁律（产出必须遵守）

- 玩法数值一律 data-driven，标注 `配表名.字段名`；还没建表的标"待配表"，**禁止硬编码和猜数**；
- 全文区分并显式标注四类陈述：**已验证事实 / 项目假设 / 估算 / 未决问题**；
- UI 按 UGUI 描述，全触控，点击热区 ≥ 44pt。

完整约束见 `shared/sr_project_context.md`。

## 四、同步上游（维护者）

上游 skill 本体不复制、不修改，以只读方式引用本仓库。同步上游与检查引用有效性的步骤见 `shared/SR_UPSTREAM.md`。同步后如有改动，`git push` 并通知成员重跑 `install.py`。

## 常见问题

**Q：我的目录结构和默认不一样（仓库不在 GameDesignOS/ 下）？**
没关系，安装时脚本会询问 workspace 实际路径，手动输入即可；或直接用 `--workspace` 参数。

**Q：换电脑/换路径后 skill 里的路径失效了？**
重跑一次 `python team-skills/install.py`，会按新路径重新替换并覆盖安装。

**Q：产出文件找不到？**
先确认安装时填的 `<SR_WORKSPACE>` 是哪个路径，所有产出都在它下面。
