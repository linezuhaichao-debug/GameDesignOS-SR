#!/usr/bin/env python3
"""安装 SR 团队工作流 skill（sr-gdd / sr-gdd-human / sr-gdd-html / sr-analysis / sr-concept / sr-config / sr-config-heroskill）。

把 team-skills/ 下的 sr-gdd、sr-gdd-human、sr-gdd-html、sr-analysis、sr-concept、sr-config、sr-config-heroskill、shared 复制到本机 skill 目录，
并将其中的 <SR_REPO>、<SR_WORKSPACE>、<SR_PROJECT> 占位符替换为本机实际路径。

安装目标默认**按当前 agent 自动识别**（不再默认往 <workspace>/.claude/skills 塞）：
  * 先看哪个被扫描根里已经装了本团队 skill —— 那就是这台机器上真正生效的根；
  * 否则取当前 agent 的用户级 skill 根（DSH → ~/.agents/skills、Claude Code → ~/.claude/skills、Codex → ~/.codex/skills）；
  * 认不出 agent 时才退回旧默认 <workspace 上两级>/.claude/skills，并对"不在扫描根"给出警告。
装在扫描根之外 skill 不会被加载，这是最常踩的坑。

用法：
    python team-skills/install.py                      # 交互式
    python team-skills/install.py --workspace PATH --project PATH [--target PATH] --yes

SKILL.md 是标准 Agent Skills 格式，任何支持该格式的工具（Claude Code、Codex 等）
都能加载；--target 指向对应工具的 skill 目录即可。
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

SKILL_DIRS = ("sr-gdd", "sr-gdd-human", "sr-gdd-html", "sr-analysis", "sr-concept",
              "sr-config", "sr-config-heroskill", "shared")
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


def nearest_git_root(start: Path) -> Path:
    """最近的含 .git 的祖先目录（与 DSH 的 projectRoot 规则一致）；找不到就用 start 自身。"""
    p = start.resolve()
    for cur in (p, *p.parents):
        if (cur / ".git").exists():
            return cur
    return p


def has_team_skills(root: Path) -> bool:
    """该根里是否已经装过本团队的 skill——用来判定这台机器上 skill 实际被哪个根加载。"""
    return (root / "sr-gdd" / "SKILL.md").is_file() or (root / "shared" / "SR_UPSTREAM.md").is_file()


def detect_agents() -> list:
    """按环境特征识别当前 agent（可能同时命中多个，排前面的是当前正在用的工具）。"""
    agents = []
    if os.environ.get("DSH_HOME") or os.environ.get("DSH_SHELL") or os.environ.get("DSH_SESSION_ID"):
        agents.append("dsh")
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        agents.append("claude-code")
    if os.environ.get("CODEX_HOME"):
        agents.append("codex")
    return agents


AGENT_LABEL = {"dsh": "DSH (DeepSeek Harness)", "claude-code": "Claude Code", "codex": "Codex"}


def agent_roots(agent: str, workspace: Path) -> list:
    """该 agent 会加载 skill 的根目录，按扫描优先级排列，元素为 (路径, 说明, 是用户级)。"""
    home = Path.home()
    project = nearest_git_root(Path.cwd())
    if agent == "dsh":
        # @deepseek-ai/dsh-skill-filesystem 只扫这几个根，且只认第一层 <name>/SKILL.md
        dsh_home = Path(os.environ["DSH_HOME"]) if os.environ.get("DSH_HOME") else home / ".dsh"
        roots = [
            (project / ".dsh" / "skills", "DSH 项目根 rank100", False),
            (project / ".agents" / "skills", "DSH 项目根 rank200", False),
            (dsh_home / "skills", "DSH 用户根 rank400（$DSH_HOME/skills）", True),
            (home / ".dsh" / "skills", "DSH 用户根 rank400（~/.dsh/skills）", True),
            (home / ".agents" / "skills", "agents 用户根 rank500（~/.agents/skills）", True),
        ]
    elif agent == "claude-code":
        roots = [
            (project / ".claude" / "skills", "Claude Code 项目根", False),
            (home / ".claude" / "skills", "Claude Code 用户根", True),
        ]
    elif agent == "codex":
        roots = [(home / ".codex" / "skills", "Codex 用户根", True)]
    else:
        roots = []
    seen, out = set(), []
    for path, why, user_scope in roots:
        key = str(path).lower()
        if key not in seen:
            seen.add(key)
            out.append((path, why, user_scope))
    return out


def detect_target(workspace: Path) -> tuple:
    """挑默认安装目标：**当前 agent 的 skill 根优先**，不再默认往 .claude/skills 塞。

    判定顺序：
      ① 若某个被扫描根里已经装了本团队的 skill，就用它（= 这台机器上真正在生效的根）；
      ② 否则取当前 agent 的用户级根（已存在的优先，都没有则用该 agent 的约定位置，届时新建）；
      ③ 认不出 agent 时，才退回旧默认 <workspace 上两级>/.claude/skills。

    返回 (目标路径, 选择理由)。
    """
    agents = detect_agents()
    for agent in agents:
        roots = agent_roots(agent, workspace)
        for path, why, _ in roots:
            if has_team_skills(path):
                return path, f"当前 agent = {AGENT_LABEL[agent]}；{why} 已装有本团队 skill"
    if agents:
        agent = agents[0]
        roots = agent_roots(agent, workspace)
        users = [(p, w) for p, w, is_user in roots if is_user]
        for path, why in users:
            if path.is_dir():
                return path, f"当前 agent = {AGENT_LABEL[agent]}；{why}（已存在）"
        if users:
            return users[-1][0], f"当前 agent = {AGENT_LABEL[agent]}；{users[-1][1]}（首次安装，将新建）"
        if roots:
            return roots[0][0], f"当前 agent = {AGENT_LABEL[agent]}；{roots[0][1]}"
    legacy = workspace.parent.parent / ".claude" / "skills"
    return legacy, "未识别出当前 agent，沿用旧默认 .claude/skills"


def is_loaded_root(target: Path, workspace: Path) -> bool:
    """目标目录是否落在当前 agent 真正会扫描的根里——落不进去 skill 就不会被加载。"""
    agents = detect_agents()
    if not agents:
        return True  # 认不出 agent，不做判断
    t = str(target.resolve()).lower()
    for agent in agents:
        for path, _, _ in agent_roots(agent, workspace):
            if t == str(path.resolve()).lower():
                return True
    return False


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


def sync_tree(src: Path, dst: Path, local_only: list, rel: str = "") -> None:
    """把 src 同步进 dst：**同名条目以 src 为准**，dst 里 src 没有的文件原样保留。

    以前这里是 `rmtree(dst)` + `copytree(src, dst)`，会把「只存在于本机、不在仓库」的文件
    一起删掉——实测踩过：sr-config 的 `profiles/timemachine.local.yaml`（本机私有配置根路径，
    gitignore 不入仓库）和本机附带的 `tools/check_pattern_fields.py` 都被删过。
    改成合并式同步后，这类本地文件不会再丢；代价是旧版残留的废弃文件不会被自动清掉，
    所以这里把「本地独有」的文件收集出来打印，让人自己判断。
    """
    if not dst.exists():
        shutil.copytree(src, dst)
        return
    src_names = {e.name for e in src.iterdir()}
    for entry in sorted(src.iterdir()):
        child_rel = f"{rel}/{entry.name}" if rel else entry.name
        target = dst / entry.name
        if entry.is_dir():
            if target.exists() and not target.is_dir():
                target.unlink()
            sync_tree(entry, target, local_only, child_rel)
        else:
            if target.is_dir():
                shutil.rmtree(target)
            shutil.copy2(entry, target)
    for entry in sorted(dst.iterdir()):
        if entry.name not in src_names:
            local_only.append(f"{rel}/{entry.name}" if rel else entry.name)


def install(workspace: Path, project: Path, target: Path) -> None:
    for legacy in LEGACY_SKILL_DIR_NAMES:
        legacy_dst = target / legacy
        if legacy_dst.exists():
            shutil.rmtree(legacy_dst)
            print(f"  已清理旧目录 {legacy_dst}（旧命名，已由 kebab-case 目录取代）")
    for name in SKILL_DIRS:
        src = TEAM_SKILLS / name
        dst = target / name
        local_only: list = []
        sync_tree(src, dst, local_only)
        for f in dst.rglob("*"):
            if f.is_file() and f.suffix in (".md", ".json", ".txt"):
                text = f.read_text(encoding="utf-8")
                if "<SR_" not in text:
                    # 没有占位符的文件不重写：既省事，也让"原样引用"的第三方/只读素材
                    # （如 sr-gdd-html 内置的渲染工具包）在安装后仍与仓库副本逐字节一致
                    # ——否则 write_text 会把 LF 行尾改写成 CRLF，sha256 校验就不成立了。
                    continue
                f.write_text(substitute(text, REPO_ROOT, workspace, project), encoding="utf-8")
        print(f"  已安装 {name} -> {dst}")
        if local_only:
            print(f"    （保留了 {len(local_only)} 个仓库里没有的本地文件，未动：{', '.join(local_only)}）")


def main() -> None:
    ap = argparse.ArgumentParser(description="安装 SR 团队工作流 skill")
    ap.add_argument("--workspace", type=Path, help="团队 workspace 路径（<SR_WORKSPACE>）")
    ap.add_argument("--project", type=Path, help="Unity 工程根目录（<SR_PROJECT>，包含 Assets/ 的目录）")
    ap.add_argument("--target", type=Path,
                    help="skill 安装目标目录；省略时按当前 agent 自动识别（DSH → ~/.agents/skills 等）")
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

    if args.target:
        target, reason = args.target.resolve(), "由 --target 指定"
    else:
        target, reason = detect_target(workspace)
    if not args.yes and not args.target:
        target = ask("skill 安装目标目录（默认已按当前 agent 自动识别；回车采用，或自行输入）", target)
        reason = "交互确认"
    print(f"安装目标 = {target}")
    print(f"  （{reason}）")
    if not is_loaded_root(target, workspace):
        print("警告: 该目录不在当前 agent 会扫描的 skill 根里——装进去也不会被加载！")
        print("      DSH 只扫 <项目根>/.dsh/skills、<项目根>/.agents/skills、~/.dsh/skills、~/.agents/skills；")
        print("      Claude Code 用 <项目根>/.claude/skills 或 ~/.claude/skills；Codex 用 ~/.codex/skills。")
        print("      按上面的路径重新执行即可（不改 --target 时 install.py 会自己挑对）。")

    if not args.yes:
        if input("确认安装？[Y/n] ").strip().lower() == "n":
            print("已取消。")
            sys.exit(1)

    target.mkdir(parents=True, exist_ok=True)
    install(workspace, project, target)
    print("\n完成。在你的 AI 工具中输入 /sr-gdd、/sr-gdd-human、/sr-gdd-html、/sr-analysis、/sr-concept 或 /sr-config 即可使用；详见 team-skills/README.md。")


if __name__ == "__main__":
    main()
