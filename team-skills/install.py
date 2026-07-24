#!/usr/bin/env python3
"""安装 SR 团队工作流 skill（sr_gdd / sr_analysis）。

把 team-skills/ 下的 sr_gdd、sr_analysis、shared 复制到本机 skill 目录，
并将其中的 <SR_REPO>、<SR_WORKSPACE> 占位符替换为本机实际路径。

用法：
    python team-skills/install.py                      # 交互式
    python team-skills/install.py --workspace PATH --target PATH --yes

SKILL.md 是标准 Agent Skills 格式，任何支持该格式的工具（Claude Code、Codex 等）
都能加载；--target 指向对应工具的 skill 目录即可。
"""

import argparse
import shutil
import sys
from pathlib import Path

SKILL_DIRS = ("sr_gdd", "sr_analysis", "shared")
REPO_ROOT = Path(__file__).resolve().parent.parent
TEAM_SKILLS = Path(__file__).resolve().parent


def detect_workspace() -> Path:
    candidates = [
        REPO_ROOT.parent / "GameDesignOS" / "workspace",      # <根>/GameDesignOS-SR 布局
        REPO_ROOT.parent.parent / "GameDesignOS" / "workspace",  # <根>/GameDesignOS/GameDesignOS-SR 布局
        REPO_ROOT.parent / "workspace",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def detect_target(workspace: Path) -> Path:
    # workspace 形如 <根>/GameDesignOS/workspace，skill 目录默认放 <根>/.claude/skills
    return workspace.parent.parent / ".claude" / "skills"


def ask(prompt: str, default: Path) -> Path:
    raw = input(f"{prompt}\n  默认: {default}\n  回车采用默认，或输入路径: ").strip()
    return Path(raw).expanduser().resolve() if raw else default


def substitute(text: str, repo: Path, workspace: Path) -> str:
    return text.replace("<SR_REPO>", str(repo)).replace("<SR_WORKSPACE>", str(workspace))


def install(workspace: Path, target: Path) -> None:
    for name in SKILL_DIRS:
        src = TEAM_SKILLS / name
        dst = target / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        for f in dst.rglob("*"):
            if f.is_file() and f.suffix in (".md", ".json", ".txt"):
                f.write_text(substitute(f.read_text(encoding="utf-8"), REPO_ROOT, workspace), encoding="utf-8")
        print(f"  已安装 {name} -> {dst}")


def main() -> None:
    ap = argparse.ArgumentParser(description="安装 SR 团队工作流 skill")
    ap.add_argument("--workspace", type=Path, help="团队 workspace 路径（<SR_WORKSPACE>）")
    ap.add_argument("--target", type=Path, help="skill 安装目标目录（如 .claude/skills）")
    ap.add_argument("--yes", action="store_true", help="全部使用默认/参数，不再询问")
    args = ap.parse_args()

    print(f"仓库路径 <SR_REPO> = {REPO_ROOT}")

    workspace = args.workspace.resolve() if args.workspace else detect_workspace()
    if not args.yes and not args.workspace:
        workspace = ask("workspace 路径 <SR_WORKSPACE>（策划案、证据、决议等产出的落盘位置）", workspace)
    print(f"workspace <SR_WORKSPACE> = {workspace}")

    target = args.target.resolve() if args.target else detect_target(workspace)
    if not args.yes and not args.target:
        target = ask("skill 安装目标目录（Claude Code 用 .claude/skills；Codex 用 ~/.codex/skills；其它工具指定其 skill 目录）", target)
    print(f"安装目标 = {target}")

    if not args.yes:
        if input("确认安装？[Y/n] ").strip().lower() == "n":
            print("已取消。")
            sys.exit(1)

    target.mkdir(parents=True, exist_ok=True)
    install(workspace, target)
    print("\n完成。在你的 AI 工具中输入 /sr_gdd 或 /sr_analysis 即可使用；详见 team-skills/README.md。")


if __name__ == "__main__":
    main()
