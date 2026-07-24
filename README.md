# GameDesignOS-SR

团队内部仓库：游戏设计工作流 skill（sr_analysis 体验诊断拆解 / sr_gdd 功能 GDD）。

## 成员上手（三步）

```bash
# 1. 克隆仓库
git clone https://github.com/linezuhaichao-debug/GameDesignOS-SR.git
cd GameDesignOS-SR

# 2. 安装工作流 skill（需要本机有 Python 3）
python team-skills/install.py

# 3. 在你的 AI 工具里使用
#    /sr_analysis <素材路径>   —— 分析录屏/截图/PV，拆竞品功能
#    /sr_gdd <主题或材料路径>  —— 出实现粒度的功能 GDD
```

安装脚本会询问两个路径，一般回车采用默认即可：

- **workspace**：策划案、证据、决议等产出的落盘位置
- **安装目标**：skill 装到哪个目录（Claude Code 用 `.claude/skills`；Codex 用 `~/.codex/skills`；其它工具指定其 skill 目录）

## 更新

```bash
git pull
python team-skills/install.py   # 重跑一次即完成更新
```

## 详细文档

安装选项、两个 skill 的完整用法、Human Gate 选项含义、产出落盘位置、常见问题：见 [team-skills/README.md](team-skills/README.md)。
