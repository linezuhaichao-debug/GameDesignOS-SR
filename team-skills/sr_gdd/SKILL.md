---
name: sr_gdd
description: 功能 GDD 工作流——把体验记录、调研、脑图、旧策划案、配置表、UE 草稿等材料写成实现粒度的功能 GDD（功能规则、配置契约、验收标准、交接清单）。当用户说"写策划案、出GDD、设计提案、功能文档"时使用。
---

# 功能 GDD 工作流（SR-GDD）

## 功能说明

**唯一输出：功能 GDD**。按本地 `resources/templates/feature-gdd.md` 模板产出实现粒度的功能开发文档（功能规则 Rn、配置契约、验收标准 AC、交接清单），面向内部团队开发落地。

不提供一页设计 / 商业立项案等其它形态；商业 pitch 模板不得套给内部功能开发文档——历史教训：模板错配会让文档近半章节只能填占位，密度显著低于功能 GDD 结构。

不编造缺失的上游材料——缺什么就列出最小缺失清单，由人决定补不补。

## 使用方法

```
/sr_gdd <主题或材料路径>
```

或直接说人话，例如"基于英雄改造v0.2.xlsx 出功能 GDD"、"把《挂机战斗》的体验记录整理成策划案"。

## 无输入时的行为

调用时未带任何主题或材料（裸 `/sr_gdd`），**不得直接进入执行流程、不得自行扫描 workspace 找题目**。先用一段话向用户说明需要什么，并停下等输入：

1. **主题**：要写哪个功能的 GDD（功能名或一句话描述）。
2. **上游材料**（有就给路径，没有就明说没有）：
   - 旧策划案 / 脑图 / 提纲（`design\` 下或任意路径）
   - 体验记录 / 证据索引 / 竞品笔记（`<SR_WORKSPACE>\evidence\` 等）
   - 配置表（.xlsx）/ UE/界面草稿
   - 相关决议记录（`<SR_WORKSPACE>\decisions\`）

用户补齐后再从第 0 步开始。

提示时同时告知材料要求：**没有哪份上游材料是硬性必须的**——最低输入是主题 + 能支撑规则粒度的描述（旧案、脑图、体验记录、配置表任一，或当场口述）；材料薄不阻塞，会触发第 2 步决议问答与 VOI 门判定。实际建议：**旧案（或同等详细度描述）+ 涉及配置表**齐备时效率最高，可直接映射进功能规则和配置契约章节；缺了也能做，只是问答轮次会多。

## 路径约定

文中所有绝对路径在仓库中以两个变量书写：`<SR_REPO>`（本仓库 GameDesignOS-SR 的克隆路径）与 `<SR_WORKSPACE>`（团队 workspace 路径）。安装脚本已将其替换为本机实际路径；手动安装时，将这两个变量整体替换为实际路径即可，无需改动其它内容。

## 执行流程

### 第 0 步 · 载入项目语境

读 `../shared/sr_project_context.md`，后续全程遵守其中的数值铁律与写作约束。
完成判据：已读完该文件。

### 第 1 步 · 资产盘点

列出用户提供的、以及 `<SR_WORKSPACE>\` 下已有的上游材料：概念与玩家承诺、体验记录、证据索引、实验结果、竞品笔记、旧策划案、生产约束。只盘点，不评价。
完成判据：产出一份材料清单（名称 + 路径），每项标注"已有 / 缺失"。

### 第 2 步 · 缺失上游检查（VOI 门 + 决议问答）

对每个缺失项问一个问题：**它的可能结果会改变决策、范围、投入或风险处置吗？**

- 会 → 列为"最小缺失 artifact"，向用户报告后**停下等补充**（除非用户明确说继续）
- 不会 → 标注"可选学习项"，不阻塞

缺失不是自动补材料的理由；写到"足够做决策"就停，不追求百科全书。

**决议问答**：功能 GDD 要达到实现粒度（R 级规则、配置契约、AC），如果输入材料只有提纲级描述（如旧案 bullet、脑图），先把会改变规则走向的关键取舍整理成**决议问题清单**（每条给候选方案 + 推荐 + 理由），请用户逐条拍板后再成稿。不替用户做设计取舍。
完成判据：每个缺失项都有 VOI 判定结论；若触发了决议问答，清单已获用户逐条拍板。

### 第 3 步 · 撰写

以 `resources/templates/feature-gdd.md` 为章节骨架依次撰写，遵循上游 `game-design-proposal-writer` 的证据纪律，并遵守 sr_project_context.md 的数值铁律与四类陈述标注（此处不复述）。

输入含旧策划案时，其内容映射进对应章节（功能详细 → 功能规则 Rn，配置表变更 → 配置契约），映射不了的差异点在文中标注。
完成判据：模板每一节都有实质内容，或显式标注缺失原因（如"待配表""未决问题"）；无留空章节。

### 第 4 步 · 治理检查

参考上游 `paranoia-ai-system-evolver` 的 SKILL.md 做检查，并按模板末尾「治理引用」节逐条填写六个引用。
完成判据：治理引用六条全部填写，无占位符残留。

### 第 5 步 · Human Gate

向用户呈现选项并等待选择，不替用户做批准类决定：

```
approve / approve_with_conditions / request_missing_evidence / revise / reject
```

用户选择后，按上游 `contracts/decision.schema.json` 把决策写为 JSON 存入 `workspace\decisions\`。写之前先读该 schema，注意：

- 全部 required 字段必须有值（refs 类字段无内容时给空数组 `[]`，不要省略）
- `decision_id` 必须匹配 `^DEC-[A-Z0-9-]{3,}$`（如 `DEC-20260723-AFK`）
- `status` 枚举与 Human Gate 选项的映射：`approve→accepted`、`reject→rejected`、`approve_with_conditions→accepted`（条件写入选项备注）、`request_missing_evidence / revise→proposed`

## 产出规范

| 产出 | 路径（`<SR_WORKSPACE>\` 下） |
|------|------|
| 功能 GDD | `proposals\<主题>_<日期>.md` |
| 决策记录（decision.schema.json） | `decisions\decision_<主题>_<日期>.json` |
| 证据与体验记录 | `evidence\` |
| 分析中间稿 | `analysis\` |

目录不存在时直接创建。日期格式 `YYYYMMDD`。

## 上游依赖（只读，勿改）

- `<SR_REPO>\game-design-proposal-writer\SKILL.md`（证据纪律 + references/）
- `<SR_REPO>\paranoia-ai-system-evolver\SKILL.md`（治理检查）
- `<SR_REPO>\contracts\decision.schema.json`（决策记录格式）

上游同步方式见 `../shared/SR_UPSTREAM.md`。
