# Six Sigma Token Saver

A Claude Code skill that reduces token usage using Six Sigma DMAIC
(Define, Measure, Analyze, Improve, Control). It treats token spend as a
process: any token that does not move the task forward is a defect.

## Contents

- `SKILL.md`: the skill itself (frontmatter plus the DMAIC workflow).

## Install

Copy the skill folder into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/six-sigma-token-saver
cp SKILL.md ~/.claude/skills/six-sigma-token-saver/SKILL.md
```

On Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills\six-sigma-token-saver" | Out-Null
Copy-Item SKILL.md "$HOME\.claude\skills\six-sigma-token-saver\SKILL.md"
```

## Usage

The skill triggers on requests about usage or rate limits, high token use,
cutting context, or optimizing prompts, tool calls, or CLAUDE.md.
