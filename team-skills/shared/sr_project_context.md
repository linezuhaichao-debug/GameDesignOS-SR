# SR 项目语境（写策划案前必读）

## 项目

- **文明之跃（Leaps of Civilization）**：移动端 SLG 策略手游
- 引擎 Unity 2022.3.62f2 + URP；C#（引擎层/确定性 sim）+ Lua/XLua（热更玩法逻辑），C# 热更经 HybridCLR
- 目标平台 Android/iOS，全触控设计，点击热区 ≥ 44pt，禁止 hover 专属交互

## 数值铁律

- 所有玩法数值 **data-driven**，来自 Excel 配表（工具链 `Assets/Scripts/Editor/ExcelConfigs/`），**禁止硬编码**
- 策划案中出现的每个数值必须标注来源：`配表名.字段名`；还没有配表的标注"待配表"
- 公式必须写出变量定义，不得只给结论数字

## 写作约束

- 中文写作；术语与项目代码命名保持一致（如 Buff、Handler、Manager 不翻译）
- 区分四类陈述并显式标注：**已验证事实 / 项目假设 / 估算 / 未决问题**
- 涉及战斗系统的设计，注意两种模式共享同一个确定性战斗引擎 RPGBattleModule（开放世界与独立战斗场景）
- UI 相关设计按 UGUI 描述，不用 UI Toolkit 概念

## 受众默认

未特别说明时，策划案受众为本团队内部（策划 + 程序），不是对外 pitch。
