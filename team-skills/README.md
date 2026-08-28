# SR 团队工作流 skill

本目录是团队内部的三个工作流 skill，方法论只读引用本仓库的上游 skill（`game-experience-analyzer`、`game-design-proposal-writer`、`game-concept-architect`、`paranoia-ai-system-evolver` 等），本目录只固化 SR 团队的项目语境、VOI 门、产出路径与 Human Gate。

| skill | 用途 | 什么时候用 |
| --- | --- | --- |
| `sr-concept` | 创新功能设计：把一句话创意扩成设计核三角报告（concept seed、玩家动词、design nucleus options、假设台账）；你拍板设计核后展开完整功能设计（玩家承诺、核心循环、scope gate、验证计划），交接给 sr-gdd | "我有个创意"、"想个新玩法"、"这个点子能不能做" |
| `sr-analysis` | 体验诊断 + 设计拆解复刻：先把录屏/截图/PV/商店页等素材分析成证据链报告；你判定"可参考"后再拆成复刻规格，交接给 sr-gdd | "分析这段录屏"、"拆一下这个竞品玩法"、"这个功能能不能复刻" |
| `sr-gdd` | 功能 GDD 工作流（完整溯源版）：把体验记录、旧策划案、脑图、配置表等材料写成实现粒度的功能 GDD（功能规则、配置契约、验收标准、交接清单），带证据溯源与治理引用 | "写策划案"、"出 GDD"、"把这个整理成功能文档" |
| `sr-gdd-human` | 功能 GDD 工作流（人类可读版）：同样产出实现粒度的功能 GDD，但不生成配置契约、不留证据/拍板/治理等过程性内容，只呈现设计结果；重点保证功能规则详细可读、界面流程完整到位 | "出一份给开发团队看的可读版 GDD"、"定稿只留规则不要过程" |
| `sr-config` | 策划配置数据契约：把确认的策划规则落实为可追溯、可确认、可读回验收的配置数据变更（新建运行时表、增删改字段/记录、同步 INDEX/说明/批注、新表测试数据、读回验收） | "把这条规则落成配置表"、"给这张表加个字段"、"建一张新配置表" |

五个 skill 共享 `shared/` 下的项目语境（`sr_project_context.md`：数值铁律、写作约束）与上游说明（`SR_UPSTREAM.md`），安装时必须六个目录一起装。

## 一、安装（团队成员）

前置：已 `git clone` 本仓库，本机有 Python 3。

```bash
cd <仓库路径>
python team-skills/install.py
```

脚本会做四件事：

1. 自动识别仓库路径（`<SR_REPO>`）；
2. 询问 workspace 路径（`<SR_WORKSPACE>`，策划案/证据/决议的落盘位置，通常自动检测正确，回车确认即可）；
3. 询问 Unity 工程根目录（`<SR_PROJECT>`，包含 `Assets/` 的目录，配表与文本表所在；自动检测 = `Assets/HotRes` 结构 + `.git` remote URL 特征匹配，与工程目录名无关，检测不到会要求手动输入）；
4. 询问安装目标目录后，把 `sr-gdd`、`sr-gdd-human`、`sr-analysis`、`sr-concept`、`sr-config`、`shared` 复制过去，并把文件里的路径变量替换成本机实际路径。

非交互安装（脚本/CI 用）：

```bash
python team-skills/install.py --workspace "D:\GameDesignOS\workspace" --project "D:\TimeMachine\PlanetRoot" --target "D:\.claude\skills" --yes
```

**用的不是 Claude Code？** SKILL.md 是标准 Agent Skills 格式，任何支持该格式的工具都能加载——把 `--target` 指到对应工具的 skill 目录即可（例如 Codex 用 `~/.codex/skills`）。工具完全不支持 skill 格式时，也可以手动复制 `sr-gdd/`、`sr-gdd-human/`、`sr-analysis/`、`sr-concept/`、`sr-config/`、`shared/` 六个目录到任意位置，把文件里的 `<SR_REPO>`、`<SR_WORKSPACE>`、`<SR_PROJECT>` 全局替换为本机路径，然后把 SKILL.md 内容作为提示词使用。

**更新**：`git pull` 后重跑一次 `install.py` 即可（会覆盖旧安装）。

## 二、使用教学

### sr-concept：从创意到功能设计

```
/sr-concept 玩家可以回溯时间改写上一场战斗的结果
```

或直接说人话："我有个创意：……"、"想个新玩法"。裸 `/sr-concept`（不带创意）不会自动开始，会先问你要创意一句话和定位（本项目新功能 / 通用概念，默认项目内）。

它会先复述创意并和你确认理解，然后产出**设计核三角报告**：concept seed、玩家动词清单、2~4 个 design nucleus 候选（各带风险与最小验证方式）、假设台账、外部证据状态。做完即停，由你在设计核门做选择：

| 选项 | 含义 |
| --- | --- |
| `pick_nucleus_<编号>` | 选定设计核，进入第二阶段展开完整功能设计 |
| `merge_nuclei` | 合并候选，回炉调整 |
| `regenerate_options` | 候选都不行，重新生成 |
| `request_external_evidence` | 关键判断缺证据，先补最小验证 |
| `stop` | 终止 |

选定设计核后才展开**功能设计稿**（玩家承诺、核心循环、关键系统、scope gate、生产可行性、验证计划、配置项预测），和你迭代到认可后，交接门选 `route_to_sr-gdd` 自动生成给 sr-gdd 的交接材料。

### sr-analysis：分析素材

```
/sr-analysis D:\recordings\新手期首战.mp4
```

或直接说人话："分析一下这段新手期录屏的前期体验"。裸 `/sr-analysis`（不带素材）不会自动开始，会先问你要素材路径和分析目标。

流程上它会先和你确认"这次分析要改变什么决策"（VOI 门），再声明样本能证明什么、不能证明什么，然后产出**证据链报告**（体验报告 + 问题卡）。做完即停，由你在报告门做选择：

| 选项 | 含义 |
| --- | --- |
| `accept_diagnosis` | 接受诊断结论，结束 |
| `enter_dissection` | 判定该功能可参考，进入设计拆解，产出复刻规格 |
| `request_more_evidence` | 证据不足，补素材再来 |
| `route_to_ed_experiment` | 转交给体验密度优化实验 |
| `revise_player_promise` | 回头修订玩家承诺 |
| `stop` | 终止 |

只有选 `enter_dissection` 才会进入第二阶段拆复刻规格；规格会和你迭代到认可后，交接门选 `route_to_sr-gdd` 自动生成给 sr-gdd 的交接材料。

### sr-gdd：出功能 GDD

```
/sr-gdd 基于 英雄改造v0.2.xlsx 出功能 GDD
```

裸 `/sr-gdd` 会先问你要主题和上游材料。**没有任何一份材料是硬性必须的**，最低输入是主题 + 一段能支撑规则粒度的描述；但"旧案（或同等详细度描述）+ 涉及配置表"齐备时效率最高。材料薄不阻塞——会触发决议问答，把关键取舍列成清单请你逐条拍板，它**不替你做设计取舍**。

成稿后的 Human Gate 选项：

| 选项 | 含义 |
| --- | --- |
| `approve` | 批准，决策记录落盘为 accepted |
| `approve_with_conditions` | 有条件批准（条件写进备注） |
| `request_missing_evidence` | 缺上游材料，先补 |
| `revise` | 打回修改 |
| `reject` | 否决 |

### sr-gdd-human：出人类可读版功能 GDD

```
/sr-gdd-human 基于 神话宝库四版GDD 出合并定稿
```

与 sr-gdd 的分工：sr-gdd 带证据溯源、配置契约、治理引用，适合正式立项留档；sr-gdd-human **只留设计结果**——不生成配置契约（表由策划自建）、不写证据/拍板编号/裁决表/台账/治理引用，重点保证功能规则（条件/动作/结果/边界齐全且一句话可读）与界面流程（每个界面 ASCII 线框图 + 逐条 UE 规则表）详细到位。适合在 sr-gdd 定稿后出"给开发团队看的执行版"，或材料充分时直接一步出可读版。

Human Gate 选项比 sr-gdd 少一个 `request_missing_evidence`（缺材料在流程内已问过）：`approve` / `approve_with_conditions` / `revise` / `reject`。

### sr-config：把策划规则落成配置数据

```
/sr-config 给英雄基础表加一个"碎片合成所需数量"字段
/sr-config 新建一张神话宝库里程碑表
```

只验收最终配置数据（运行时表与五行表头、字段与记录、主键与索引、枚举、codec、引用、INDEX、配置说明、字段批注、新表测试数据）。流程：确定任务范围（新建表/字段变更/记录变更三选一或多选）→ 建立证据与契约（必须读取单元格批注，附 `tools/probe_workbook.py` 标准探查工具）→ 生成 change set 过确认门 → 新表自动生成测试数据 → 备份-写入-读回 100% 验收（附 `tools/readback_report_template.md` 模板）。

状态机：`DRAFT → PASS / BLOCKED`，`blocking_items` 清空才能写入，只有 `PASS` 算完成。本机配置根目录写在 `sr-config/profiles/timemachine.local.yaml`（含私有路径，不入仓库；首次使用参照同目录 `timemachine.local.example.yaml` 创建）。

### 典型流水线

```
一句话创意 ──────► /sr-concept ──► 设计核三角报告 ──(pick_nucleus)──► 功能设计稿
                                                              │
竞品录屏/截图 ──► /sr-analysis ──► 证据链报告 ──(enter_dissection)──► 复刻规格
                                                              │
                                              (route_to_sr-gdd)│
                                                              ▼
旧策划案/配置表 ────────────────────────────────► /sr-gdd ──► 功能 GDD ──► 开发排期
                                                              │
                                              (需要可读执行版)│
                                                              ▼
                                              /sr-gdd-human ──► 人类可读版 GDD（无溯源/配置契约）
```

### 产出落盘位置

所有产出写入 `<SR_WORKSPACE>` 下（安装时确定）：

| 产出 | 子目录 |
| --- | --- |
| 功能 GDD | `proposals\` |
| 设计核三角报告 / 功能设计稿 | `analysis\` |
| 体验报告 / 问题卡 / 复刻规格 / 交接 JSON | `analysis\` |
| 证据包（证据索引、时间戳账本） | `evidence\` |
| 决策记录（decision.schema.json） | `decisions\` |

## 三、数值铁律（产出必须遵守）

- 玩法数值一律 data-driven，标注 `配表名.字段名`；还没建表的标"待配表"，**禁止硬编码和猜数**；
- 全文区分并显式标注四类陈述：**已验证事实 / 项目假设 / 估算 / 未决问题**；

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
