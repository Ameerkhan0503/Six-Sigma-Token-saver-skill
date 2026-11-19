---
name: six-sigma-token-saver
description: Cut Claude Code token usage with Six Sigma DMAIC, starting from a measured baseline (bundled audit script ranks CLAUDE.md, plugins, skills and MCP servers by per-message cost). Use whenever the user hits usage or rate limits, says the Pro plan runs out fast, sessions feel expensive or slow, or asks to save tokens, shrink context, trim CLAUDE.md, or reduce plugins, MCP servers or tool calls, even if they never say Six Sigma.
---

# Six Sigma Token Saver

Token spend is a process; a defect is any token that does not move work forward. Most waste comes from two places, and they need different fixes:

- **Fixed baseline**: what loads on *every* message before the user types (CLAUDE.md, rules, plugin skill/agent descriptions, MCP tool schemas). Paid on every turn, so it compounds. Usually the biggest lever.
- **Session habits**: long histories, whole-file reads, noisy command output, rework. Paid per task.

Measure first, fix the largest defect, re-measure. Don't skip measuring: guesses about where tokens go are usually wrong.

## D: Define (one line each)
Goal (what runs out, e.g. "5-hour limit gone by noon"), scope (which projects or task types), target (e.g. "cut fixed baseline by half").

## M: Measure
1. Run the audit script from this skill's folder (read-only, no network):
   `python <skill-dir>/scripts/token_audit.py --project <project-dir>`
   It ranks instruction files, enabled plugins, user skills and MCP servers by estimated per-message cost. Plugin/skill figures are upper bounds (Claude Code trims long skill lists), so use them to rank, not as exact totals.
2. Get real numbers. If a usage tool is available (e.g. `get_usage` in the desktop app), call it: it returns context tokens by category and plan-limit percentages. Otherwise ask the user to run `/context` and `/cost` and paste the result, since slash commands are theirs to type.
3. Record the baseline: total context tokens, the top 3 categories, plan-limit %.

## A: Analyze
Match the biggest numbers to causes. Usual suspects, in order of typical size:
- Many plugins enabled. Disabling one saves its **agent descriptions and the text its hooks inject at session start**, not its skills: Claude Code caps the skill listing, so freed skill space is refilled by other plugins. Measured: turning off one large plugin (72 agents, startup hooks) cut a fresh session from 104,648 to 92,594 tokens (-11.5%); agents fell 57%, startup messages 19%, skills did not change.
- MCP servers the project never uses
- Long CLAUDE.md or rules files written as essays
- Long sessions without `/clear`; whole-file reads; unbounded Grep/Bash output; rework from vague requests

For the full defect-to-fix catalog and exact config commands, read `references/fixes.md`.

## I: Improve
Apply the highest-impact fix first and show the user exactly what changes. Config edits (disabling plugins, removing MCP servers, trimming CLAUDE.md) change their setup, so propose the change, get a yes, then apply it. Quick wins:
1. **Disable unused plugins**, starting with the audit's top-ranked (most agent/command text, has hooks). Scope by project if needed.
2. **Remove or scope unused MCP servers.**
3. **Trim instruction files** to facts and commands; move rare detail into a skill, which loads only when triggered.
4. **`/clear` between unrelated tasks; `/compact <focus>`** when a long task must continue.
5. **Read narrowly, cap output**: `Read` with offset/limit, Grep `files_with_matches` first, pipe noisy commands through `tail`/`grep`.

## C: Control
- Re-run the audit and the usage check; compare with the baseline. Plugin changes apply only to new sessions, so measure in a fresh one. A clean A/B: start a fresh session, have it call the usage tool on itself and report; change one setting (e.g. a project `.claude/settings.json`); repeat; compare.
- Offer to add the short habits block from `references/fixes.md` to CLAUDE.md so the gains stick.
- Re-audit after installing new plugins.

## When this skill won't help
A short one-off task has little to cut, and loading this skill itself costs about 1k tokens. In a measured A/B test on a small single-file task, the run with the skill used 1.4% *more* tokens. Say so instead of forcing DMAIC on a tiny task.

## Report format
- Baseline (numbers from M)
- Top causes (short table)
- Changes made or proposed, one line each, with estimated savings
- How to verify (which command to re-run)
