#!/usr/bin/env python3
"""Estimate the fixed token cost Claude Code pays on every message.

Read-only. Looks at local config only (no network) and reports what is loaded
into context before you type anything: instruction files (CLAUDE.md, rules),
skill and agent descriptions from enabled plugins and user skills, and MCP
servers. Token counts are estimates (characters / 4); use /context for exact
numbers. Plugin and skill figures are an UPPER BOUND: Claude Code trims long
skill listings, so the real cost is often a third or less. Use them to rank
what to disable, not as exact totals.

Usage:
    python token_audit.py [--project DIR] [--claude-home DIR] [--json] [--top N]
"""
import argparse
import json
import sys
from pathlib import Path

CHARS_PER_TOKEN = 4


def est(chars):
    return (chars + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def load_json(path):
    try:
        return json.loads(read_text(path) or "{}")
    except json.JSONDecodeError:
        return {}


def frontmatter_description(md_path):
    """Return the description text from a SKILL.md / agent .md frontmatter."""
    text = read_text(md_path)
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    out, grabbing = [], False
    for line in text[3:end].splitlines():
        if not grabbing and line.startswith("description:"):
            out.append(line[len("description:"):].strip().strip("\"'>|-"))
            grabbing = True
        elif grabbing:
            if line and not line[0].isspace():
                break
            out.append(line.strip())
    return " ".join(p for p in out if p)


def norm(p):
    return str(p).replace("\\", "/").rstrip("/").lower()


def instruction_files(home, project):
    files = [home / "CLAUDE.md"]
    if (home / "rules").is_dir():
        files += sorted((home / "rules").rglob("*.md"))
    # Project memory files: walk from the project dir up to the filesystem root.
    d, seen = project.resolve(), set()
    while True:
        for name in ("CLAUDE.md", "CLAUDE.local.md", ".claude/CLAUDE.md"):
            f = d / name
            if f.is_file() and norm(f) not in seen:
                files.append(f)
                seen.add(norm(f))
        if d.parent == d:
            break
        d = d.parent
    rules = project / ".claude" / "rules"
    if rules.is_dir():
        files += sorted(rules.rglob("*.md"))
    rows, done = [], set()
    for f in files:
        if f.is_file() and norm(f.resolve()) not in done:
            done.add(norm(f.resolve()))
            chars = len(read_text(f))
            rows.append({"item": str(f), "chars": chars, "tokens": est(chars)})
    rows.sort(key=lambda r: r["tokens"], reverse=True)
    return rows


def enabled_plugins(home, project):
    enabled = {}
    for s in (home / "settings.json", project / ".claude" / "settings.json",
              project / ".claude" / "settings.local.json"):
        for name, on in load_json(s).get("enabledPlugins", {}).items():
            enabled[name] = bool(on)  # later files override earlier ones
    return [n for n, on in enabled.items() if on]


def plugin_install_paths(home):
    data = load_json(home / "plugins" / "installed_plugins.json")
    out = {}
    for name, entries in data.get("plugins", {}).items():
        if isinstance(entries, list) and entries:
            out[name] = Path(entries[-1].get("installPath", ""))
    return out


def describe_dir(root):
    """Sum description sizes for skills, agents and commands under a plugin root."""
    counts = {"skills": 0, "agents": 0, "commands": 0}
    chars = 0
    for kind, pattern in (("skills", "skills/*/SKILL.md"),
                          ("agents", "agents/*.md"),
                          ("commands", "commands/*.md")):
        for f in root.glob(pattern):
            counts[kind] += 1
            label = f.parent.name if kind == "skills" else f.stem
            chars += len(frontmatter_description(f)) + len(label) + 20
    mcp = list(load_json(root / ".mcp.json").get("mcpServers", {}).keys())
    return counts, chars, mcp


def plugin_rows(home, project):
    paths = plugin_install_paths(home)
    rows = []
    for name in enabled_plugins(home, project):
        root = paths.get(name)
        if not root or not root.is_dir():
            rows.append({"item": name, "tokens": 0, "note": "install path not found"})
            continue
        counts, chars, mcp = describe_dir(root)
        rows.append({"item": name, "chars": chars, "tokens": est(chars),
                     "skills": counts["skills"], "agents": counts["agents"],
                     "commands": counts["commands"], "mcp_servers": mcp})
    rows.sort(key=lambda r: r["tokens"], reverse=True)
    return rows


def user_skill_rows(home, project):
    rows = []
    for base in (home / "skills", project / ".claude" / "skills"):
        if not base.is_dir():
            continue
        for f in sorted(base.glob("*/SKILL.md")):
            chars = len(frontmatter_description(f)) + len(f.parent.name) + 20
            rows.append({"item": f.parent.name, "chars": chars, "tokens": est(chars)})
    rows.sort(key=lambda r: r["tokens"], reverse=True)
    return rows


def mcp_servers(home, project, plugins):
    servers = []
    cfg = load_json(home.parent / ".claude.json")
    servers += [(n, "user") for n in cfg.get("mcpServers", {})]
    pkey = norm(project.resolve())
    for path, pcfg in cfg.get("projects", {}).items():
        if norm(path) == pkey:
            servers += [(n, "project-local") for n in pcfg.get("mcpServers", {})]
    servers += [(n, "project .mcp.json") for n in
                load_json(project / ".mcp.json").get("mcpServers", {})]
    for p in plugins:
        servers += [(n, "plugin " + p["item"]) for n in p.get("mcp_servers", [])]
    return [{"item": n, "source": s} for n, s in servers]


def recommendations(instr, plugins, mcps):
    recs = []
    instr_tok = sum(r["tokens"] for r in instr)
    if instr_tok > 1500:
        big = instr[0]
        recs.append(f"Instruction files cost ~{instr_tok} tokens per message. "
                    f"Largest: {big['item']} (~{big['tokens']}). Cut essays down to facts "
                    f"and commands; move rarely needed detail into a skill.")
    plug_tok = sum(r["tokens"] for r in plugins)
    if len(plugins) > 8 or plug_tok > 4000:
        heavy = ", ".join(f"{r['item']} (~{r['tokens']})" for r in plugins[:5])
        recs.append(f"{len(plugins)} plugins enabled, up to ~{plug_tok} tokens of skill/"
                    f"agent/command descriptions per message (upper bound). Heaviest: "
                    f"{heavy}. Disable the "
                    f"ones this project does not use (enabledPlugins in settings.json; "
                    f"use the project's .claude/settings.json to scope per project).")
    if len(mcps) > 3:
        names = ", ".join(m["item"] for m in mcps)
        recs.append(f"{len(mcps)} MCP servers configured ({names}). Each adds its tool "
                    f"schemas to every message, often 1-10k tokens. Remove or scope the "
                    f"unused ones; /context shows the real per-server cost.")
    if not recs:
        recs.append("Fixed baseline looks lean. Savings now come from session habits: "
                    "/clear between tasks, narrow reads, capped command output.")
    return recs


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", default=".", help="project directory (default: cwd)")
    ap.add_argument("--claude-home", default=str(Path.home() / ".claude"))
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--top", type=int, default=8, help="rows to show per section")
    a = ap.parse_args()

    home, project = Path(a.claude_home), Path(a.project)
    instr = instruction_files(home, project)
    plugins = plugin_rows(home, project)
    skills = user_skill_rows(home, project)
    mcps = mcp_servers(home, project, plugins)
    total = sum(r["tokens"] for r in instr + plugins + skills)
    report = {
        "fixed_tokens_upper_bound_excluding_mcp": total,
        "instruction_files": instr,
        "plugins": plugins,
        "user_skills": skills,
        "mcp_servers": mcps,
        "recommendations": recommendations(instr, plugins, mcps),
    }
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    if a.json:
        print(json.dumps(report, indent=2))
        return

    print("Token baseline audit (estimates: chars/4; /context gives exact numbers)")
    print(f"Fixed cost per message, excluding MCP tool schemas: up to ~{total} tokens")
    print("(Plugin/skill figures are upper bounds; Claude Code trims long skill lists.\n"
          " Use them to rank what to disable.)\n")

    def section(title, rows, extra=None):
        sub = sum(r.get("tokens", 0) for r in rows)
        print(f"{title}: {len(rows)} item(s), ~{sub} tokens")
        for r in rows[:a.top]:
            tail = f"  [{extra(r)}]" if extra else ""
            print(f"  ~{r.get('tokens', 0):>6}  {r['item']}{tail}")
        if len(rows) > a.top:
            print(f"  ... {len(rows) - a.top} more")
        print()

    section("Instruction files (CLAUDE.md, rules)", instr)
    section("Enabled plugins (descriptions)", plugins,
            lambda r: r.get("note") or f"{r['skills']} skills, {r['agents']} agents, "
                                         f"{r['commands']} commands")
    section("User skills (descriptions)", skills)
    print(f"MCP servers: {len(mcps)} (tool schema cost not measurable offline)")
    for m in mcps:
        print(f"  {m['item']}  ({m['source']})")
    print("\nRecommendations:")
    for i, r in enumerate(report["recommendations"], 1):
        print(f"  {i}. {r}")


if __name__ == "__main__":
    main()
