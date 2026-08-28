#!/usr/bin/env python3
"""安装 SR 团队工作流 skill（sr-gdd / sr-gdd-human / sr-analysis / sr-concept）。

把 team-skills/ 下的 sr-gdd、sr-gdd-human、sr-analysis、sr-concept、shared 复制到本机 skill 目录，
并将其中的 <SR_REPO>、<SR_WORKSPACE>、<SR_PROJECT> 占位符替换为本机实际路径。

用法：
    python team-skills/install.py                      # 交互式
    python team-skills/install.py --workspace PATH --project PATH --target PATH --yes

SKILL.md 是标准 Agent Skills 格式，任何支持该格式的工具（Claude Code、Codex 等）
都能加载；--target 指向对应工具的 skill 目录即可。
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

SKILL_DIRS = ("sr-gdd", "sr-gdd-human", "sr-analysis", "sr-concept", "shared")
REPO_ROOT = Path(__file__).resolve().parent.parent
TEAM_SKILLS = Path(__file__).resolve().parent

# SR Unity 工程仓库 remote URL 的特征子串（小写包含匹配）。
# 本机可能有多个 Unity 工程，Assets/HotRes 结构不足以区分；
# 若工程仓库迁移或改名，改这里即可。
PROJECT_GIT_URL_HINT = "projectreclaimnew"


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


def git_remote_urls(path: Path) -> list:
    """读取 <path>/.git/config 中的 remote URL；worktree（.git 为文件）或无仓库时返回空。"""
    config = path / ".git" / "config"
    if not config.is_file():
        return []
    return re.findall(r"^\s*url\s*=\s*(\S+)\s*$",
                      config.read_text(encoding="utf-8", errors="ignore"), re.M)


def is_sr_project(path: Path) -> bool:
    return any(PROJECT_GIT_URL_HINT in url.lower() for url in git_remote_urls(path))


def detect_project() -> Path:
    """探测 Unity 工程根：仓库邻近目录中含 Assets/HotRes 的目录。

    优先返回 .git remote URL 匹配 PROJECT_GIT_URL_HINT 的候选；
    无匹配时回退到第一个结构候选（调用方应提示用户确认），都没有返回 None。
    """
    candidates = []
    for root in (REPO_ROOT.parent, REPO_ROOT.parent.parent):
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if child.is_dir() and (child / "Assets" / "HotRes").is_dir():
                candidates.append(child)
    for c in candidates:
        if is_sr_project(c):
            return c
    return candidates[0] if candidates else None


def detect_target(workspace: Path) -> Path:
    # workspace 形如 <根>/GameDesignOS/workspace，skill 目录默认放 <根>/.claude/skills
    return workspace.parent.parent / ".claude" / "skills"


def ask(prompt: str, default: Path = None) -> Path:
    hint = f"  默认: {default}\n  回车采用默认，或输入路径: " if default else "  未自动检测到，请输入路径: "
    while True:
        raw = input(f"{prompt}\n{hint}").strip()
        if raw:
            return Path(raw).expanduser().resolve()
        if default is not None:
            return default


def substitute(text: str, repo: Path, workspace: Path, project: Path) -> str:
    text = (text.replace("<SR_REPO>", str(repo))
                .replace("<SR_WORKSPACE>", str(workspace))
                .replace("<SR_PROJECT>", str(project)))
    if os.sep != "/":
        # 源文件中占位符后的路径段用正斜杠书写（如 <SR_PROJECT>/Assets/...），
        # Windows 上替换后会出现混合分隔符，这里统一为 os.sep
        for root in (repo, workspace, project):
            text = re.sub(re.escape(str(root)) + r"((?:[/\\][\w.\-]+)+[/\\]?)",
                          lambda m: str(root) + m.group(1).replace("/", os.sep), text)
    return text


# 旧版 skill 目录名（下划线命名，2026-07 起已改为 kebab-case，如 sr_gdd -> sr-gdd）。
# DSH 等工具要求 skill 名必须为 kebab-case；保留旧名清理以免新旧目录并存导致重复加载。
LEGACY_SKILL_DIR_NAMES = ("sr_gdd", "sr_analysis", "sr_concept")


def install(workspace: Path, project: Path, target: Path) -> None:
    for legacy in LEGACY_SKILL_DIR_NAMES:
        legacy_dst = target / legacy
        if legacy_dst.exists():
            shutil.rmtree(legacy_dst)
            print(f"  已清理旧目录 {legacy_dst}（旧命名，已由 kebab-case 目录取代）")
    for name in SKILL_DIRS:
        src = TEAM_SKILLS / name
        dst = target / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        for f in dst.rglob("*"):
            if f.is_file() and f.suffix in (".md", ".json", ".txt"):
                f.write_text(substitute(f.read_text(encoding="utf-8"), REPO_ROOT, workspace, project), encoding="utf-8")
        print(f"  已安装 {name} -> {dst}")


def main() -> None:
    ap = argparse.ArgumentParser(description="安装 SR 团队工作流 skill")
    ap.add_argument("--workspace", type=Path, help="团队 workspace 路径（<SR_WORKSPACE>）")
    ap.add_argument("--project", type=Path, help="Unity 工程根目录（<SR_PROJECT>，包含 Assets/ 的目录）")
    ap.add_argument("--target", type=Path, help="skill 安装目标目录（如 .claude/skills）")
    ap.add_argument("--yes", action="store_true", help="全部使用默认/参数，不再询问")
    args = ap.parse_args()

    print(f"仓库路径 <SR_REPO> = {REPO_ROOT}")

    workspace = args.workspace.resolve() if args.workspace else detect_workspace()
    if not args.yes and not args.workspace:
        workspace = ask("workspace 路径 <SR_WORKSPACE>（策划案、证据、决议等产出的落盘位置）", workspace)
    print(f"workspace <SR_WORKSPACE> = {workspace}")

    project = args.project.resolve() if args.project else detect_project()
    if not args.yes and not args.project:
        project = ask("Unity 工程根目录 <SR_PROJECT>（包含 Assets/ 的目录，配表与文本表所在）", project)
    if project is None:
        print("错误: 未指定 Unity 工程根目录。请用 --project PATH 指定，或交互模式下手动输入。")
        sys.exit(1)
    print(f"Unity 工程 <SR_PROJECT> = {project}")
    if not is_sr_project(project):
        print(f"注意: 该工程 .git remote 未匹配特征 {PROJECT_GIT_URL_HINT!r}，请确认是否为本项目 Unity 工程。")
    if not (project / "Assets" / "HotRes").is_dir():
        print(f"警告: {project} 下未找到 Assets/HotRes，配表路径可能不正确，请确认。")

    target = args.target.resolve() if args.target else detect_target(workspace)
    if not args.yes and not args.target:
        target = ask("skill 安装目标目录（Claude Code 用 .claude/skills；Codex 用 ~/.codex/skills；其它工具指定其 skill 目录）", target)
    print(f"安装目标 = {target}")

    if not args.yes:
        if input("确认安装？[Y/n] ").strip().lower() == "n":
            print("已取消。")
            sys.exit(1)

    target.mkdir(parents=True, exist_ok=True)
    install(workspace, project, target)
    print("\n完成。在你的 AI 工具中输入 /sr-gdd、/sr-gdd-human、/sr-analysis 或 /sr-concept 即可使用；详见 team-skills/README.md。")


if __name__ == "__main__":
    main()
