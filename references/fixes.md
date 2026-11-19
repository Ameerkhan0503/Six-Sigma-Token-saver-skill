# Fix catalog

Read this when the audit or usage numbers point at a cause and you need the exact fix.

## Contents
1. Defect-to-cause table
2. Fixed-baseline fixes (plugins, MCP, instruction files)
3. Session-habit fixes
4. CLAUDE.md habits block (for Control)

## 1. Defect-to-cause table

| Defect (what you see) | Root cause | Fix |
|---|---|---|
| Large "Skills" / "Custom agents" / "Commands" in `/context` | Many plugins enabled | 2a |
| Large "MCP tools" in `/context` | MCP servers enabled but unused | 2b |
| Large "Memory files" / instruction share | Long CLAUDE.md or rules | 2c |
| "Messages" grows fast | Long session, no `/clear` | 3a |
| Same file read repeatedly | Session too long, no plan | 3a, 3e |
| Huge tool results | Whole-file reads, unbounded Grep/Bash | 3b, 3c |
| Retries and corrections | Vague first request, no plan | 3e |
| Large model on easy work | No model right-sizing | 3f |
| Agents spawned for small lookups | Subagent overuse | 3g |

## 2. Fixed-baseline fixes

These cost tokens on every message in every session, so a small cut here beats a big cut in one task. Always show the user the exact change and get a yes before editing their config.

### 2a. Plugins
- Rank by the audit script's plugin section, which orders plugins by agent/command text and hooks. That is what disabling saves: Claude Code caps the skill listing, so removing a plugin's skills just lets other skills refill the space.
- Measured example: disabling one plugin with 72 agents and startup hooks cut a fresh session from 104,648 to 92,594 tokens (-11.5%). Custom agents -5,501, startup messages -6,536, skills +144 (refilled).
- Disable globally: in `~/.claude/settings.json`, set `"enabledPlugins": { "<name>@<marketplace>": false }`, or use the `/plugin` menu.
- Disable for one project only: put the same entry in that project's `.claude/settings.json`. Project settings override user settings, so a plugin can stay on elsewhere.
- Plugins with hooks can inject sizeable text at session start (it shows up under "Messages" in `/context`); weigh that too.
- Changes apply to new sessions only; measure in a fresh one.

### 2b. MCP servers
- List: `claude mcp list`. Remove a user-scoped server: `claude mcp remove <name> -s user`. Toggle within a session: `/mcp`.
- Servers bundled in a plugin go away when the plugin is disabled.
- Each server's tool schemas load every message; servers with many tools commonly cost several thousand tokens.

### 2c. Instruction files (CLAUDE.md, rules)
- Keep to facts and commands the model can't infer: build/test commands, conventions, gotchas. Drop essays, rationale paragraphs, and duplicated tool docs.
- Move rarely needed procedures into a skill: only its short description is always loaded; the body loads on demand.
- Avoid editing CLAUDE.md mid-session; it breaks prompt caching for the next turn.

## 3. Session-habit fixes

- **3a. Reset context.** `/clear` at each unrelated task boundary. `/compact <what to keep>` when a long task must continue past about half the window.
- **3b. Read narrowly.** `Read` with `offset`/`limit` for known ranges; Grep with `output_mode: "files_with_matches"` and `head_limit` first, then open only the hits.
- **3c. Cap command output.** Pipe through `tail -n 40`, `grep -E "FAIL|Error"`, or quiet flags (`-q`, `--silent`).
- **3d. Edit, don't rewrite.** `Edit` for changes; `Write` only for new files. Give paths instead of pasting files into chat.
- **3e. Precise first request, plan once.** State file, expected result, done condition. For multi-file work, agree the plan once, then execute.
- **3f. Right-size the model.** Smaller model for lookups, renames, formatting; largest for hard design or debugging (`/model`).
- **3g. Subagents only for broad searches** that would otherwise flood the main context. One targeted Grep beats an agent.
- **3h. Batch independent calls** in one message.

## 4. CLAUDE.md habits block (for Control)

Offer to append this to the user's CLAUDE.md (about 80 tokens):

```markdown
## Token habits
- /clear between unrelated tasks; /compact <focus> past half the window.
- Read with offset/limit; Grep files_with_matches first; cap command output with tail/grep.
- Edit existing files instead of rewriting; give paths, don't paste files.
- Re-audit (six-sigma-token-saver) after installing plugins or MCP servers.
```
