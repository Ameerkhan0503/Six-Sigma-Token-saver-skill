---
name: six-sigma-token-saver
description: Reduce Claude Code token usage using Six Sigma DMAIC (Define, Measure, Analyze, Improve, Control). Use this whenever the user says they are hitting usage or rate limits, the Pro plan runs out fast, token use is high, sessions are expensive or slow, they ask to save tokens, cut context, reduce waste, or optimize prompts, tool calls, or CLAUDE.md, even if they do not name Six Sigma.
---

# Six Sigma Token Saver

Treat token spend as a process with defects. A "defect" is any token that does not move the task forward: re-read files, repeated context, verbose output, unneeded tool calls, or rework from vague prompts. Work through DMAIC, then keep the gains with controls.

## D: Define
State in one line each:
- The goal: what is running out (for example, "Pro limit hit by 2pm").
- The scope: which sessions, projects, or task types.
- The target: a measurable cut (for example, "halve tokens per task").

## M: Measure
Find where tokens go before changing anything:
- Run `/context` to see what fills the window (system prompt, tools, MCP servers, CLAUDE.md, history).
- Check usage in settings or with `/cost` for per-session totals.
- Note the biggest contributors: long history, big pasted content, many MCP tools, large file reads, subagent runs.

Record a baseline (for example, "session X: 180k tokens for 6 edits").

## A: Analyze
Match the biggest defects to root causes:

| Defect | Root cause |
|---|---|
| Same file read again and again | No memory of what was read; session too long |
| Huge tool output | Unbounded Grep or Bash output, reading whole files |
| Context bloat every turn | Long session history, no `/clear` between tasks |
| Heavy baseline on every message | Long CLAUDE.md or rules, many MCP servers and plugins enabled |
| Rework and retries | Vague request, no plan before big changes |
| Expensive model on easy work | Opus used for simple lookups or edits |
| Subagent overuse | Fan-out for a question one search could answer |

## I: Improve
Apply the fixes that match the root causes, highest impact first.

1. **Reset context often.** Run `/clear` when switching to an unrelated task. Run `/compact` with a focus (for example, `/compact keep the auth refactor decisions`) when a long task must continue.
2. **Read narrowly.** Use `Read` with `offset` and `limit` for known line ranges. Use `Grep` with `head_limit` and `output_mode: "files_with_matches"` first, then open only the hits.
3. **Cap command output.** Pipe noisy commands through `tail`, `head`, or `grep` (for example, show only failing test lines). Use quiet flags for builds and installs.
4. **Edit, don't rewrite.** Use `Edit` for changes to existing files. Use `Write` only for new files or full rewrites. Never paste whole files into the chat; give the path.
5. **Batch independent calls.** Send independent reads and searches in one message so they run in parallel rather than as separate round trips.
6. **Write precise prompts.** State the file, the expected result, and the done condition in the first message. One clear request beats three corrections.
7. **Plan before big work.** For multi-file changes, agree the plan once (plan mode), then execute without re-explaining.
8. **Right-size the model.** Use a smaller model for lookups, renames, formatting, and simple edits. Reserve the largest model for hard design or debugging. Switch with `/model`.
9. **Subagents only for broad search.** A single targeted Grep beats spawning an agent. Use agents when a search would otherwise flood the main context.
10. **Trim the baseline.** Keep CLAUDE.md and rules short (facts and commands, not essays). Disable MCP servers and plugins the project does not use. Each enabled tool adds cost to every message.
11. **Keep answers tight.** Ask for the result, not a recap. Skip restating the request and trailing summaries.
12. **Keep the prefix stable.** Avoid editing CLAUDE.md or switching tools mid-session, which breaks prompt caching and costs more on the next turn.

## C: Control
Keep the gains from slipping back:
- Re-measure with `/context` after each change and compare with the baseline from M.
- Use a rule: `/clear` at each task boundary, and `/compact` when the window passes about half full.
- Review CLAUDE.md and enabled MCP servers monthly. Remove what is no longer used.
- Log before and after numbers so the trend is visible.

## Output format
When applying this skill, report back briefly:
- Baseline measured (numbers from M)
- Root causes found (short table or list)
- Changes made, one line each
- Expected saving and how to verify it in C

Do not run a heavy evaluation loop for this skill unless the user asks. Measure, change, re-measure.
