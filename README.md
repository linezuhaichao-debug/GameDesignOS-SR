# GameDesignOS-SR

团队内部仓库：游戏设计工作流 skill（sr-concept 创意扩功能设计 / sr-analysis 体验诊断拆解 / sr-gdd 功能 GDD）。

## 成员上手（三步）

```bash
# 1. 克隆仓库
git clone https://github.com/linezuhaichao-debug/GameDesignOS-SR.git
cd GameDesignOS-SR

# 2. 安装工作流 skill（需要本机有 Python 3）
python team-skills/install.py

# 3. 在你的 AI 工具里使用
#    /sr-concept <一句话创意>    —— 创意扩成设计核三角报告，拍板后展开功能设计，交接 /sr-gdd
#    /sr-analysis <素材路径>     —— 分析录屏/截图/PV，判定可参考后拆复刻规格，交接 /sr-gdd
#    /sr-gdd <主题或材料路径>    —— 出实现粒度的功能 GDD
```

安装脚本会询问三个路径，一般回车采用默认即可：

- **workspace**：策划案、证据、决议等产出的落盘位置
- **Unity 工程根目录**：包含 `Assets/` 的目录，配表与文本表所在（自动检测不到会要求手动输入）
- **安装目标**：skill 装到哪个目录（Claude Code 用 `.claude/skills`；Codex 用 `~/.codex/skills`；其它工具指定其 skill 目录）

## 更新

```bash
git pull
python team-skills/install.py   # 重跑一次即完成更新
```

## 详细文档

> **三个 skill 的完整用法都在 [team-skills/README.md](team-skills/README.md)，装完建议先读一遍。**

涵盖：安装选项说明、sr-concept / sr-analysis / sr-gdd 各自的完整流程与 Human Gate 选项含义、典型流水线（创意→设计核→GDD）、产出落盘位置、数值铁律、常见问题。
