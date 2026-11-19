# Six Sigma Token Saver

A Claude Code skill that cuts token usage with Six Sigma DMAIC (Define,
Measure, Analyze, Improve, Control). It starts from a measured baseline
instead of generic tips: a bundled audit script ranks what you pay for on
every message, so you fix the biggest defect first.

## Contents

- `SKILL.md`: the workflow Claude follows (kept short; loads only when triggered).
- `scripts/token_audit.py`: read-only audit of your fixed per-message cost.
- `references/fixes.md`: defect-to-fix catalog with exact config commands and a
  CLAUDE.md habits block. Claude reads it only when needed.

## Install

macOS / Linux:

```bash
mkdir -p ~/.claude/skills
cp -r . ~/.claude/skills/six-sigma-token-saver
```

Windows (PowerShell):

```powershell
Copy-Item -Recurse -Force . "$HOME\.claude\skills\six-sigma-token-saver"
```

Start a new Claude Code session afterwards so the skill list refreshes.

## Run the audit yourself

```bash
python scripts/token_audit.py --project /path/to/your/project
```

Add `--json` for machine-readable output. It needs only Python 3, reads local
config, and makes no network calls. It reports:

- instruction files (`CLAUDE.md`, rules) with estimated tokens
- enabled plugins ranked by skill/agent/command description size
- user skills
- configured MCP servers
- recommendations based on what is largest

Token figures are estimates (characters / 4). Plugin and skill figures are
upper bounds, because Claude Code trims long skill listings; use them to rank
what to disable. `/context` gives exact numbers.

## Usage

Ask Claude things like "my Pro limit runs out by noon", "why is every message
so expensive", or "trim my CLAUDE.md". The skill measures, ranks causes,
proposes fixes (asking before it changes your config), and tells you how to
verify the saving.

## Measured results

| Test | Without skill | With skill | Result |
|---|---|---|---|
| Small one-off task (draw a single SVG file), fresh agent each | 84,739 tokens | 85,884 tokens | +1.4%: no saving |

Conclusion: the skill does not help short one-off tasks; loading it costs
about 1k tokens. It is aimed at the fixed baseline and long sessions. On the
author's machine the audit found 23 enabled plugins, with one plugin
accounting for roughly 65% of all description text, and 5 MCP servers.
Disabling unused ones of those is where real savings are expected. That
saving has not been measured yet; re-run the audit and `/context` before and
after to verify it on your setup.

## Changelog

- v2: added the audit script and fix catalog; trimmed SKILL.md; added the
  "when this won't help" section based on the A/B test.
- v1: initial DMAIC skill.
