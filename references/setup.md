# Setup and Installation Notes

This skill is portable across Agent-Skills-compatible coding agents. Keep one canonical copy and symlink it into each agent's skill directory.

## Runtime requirement

The skill expects the `fastcontext` CLI on `PATH` or a FastContext MCP tool such as `fastcontext_explore`.

For the CLI backend, configure an OpenAI-compatible FastContext model endpoint in your shell. The wrapper accepts either variable family and mirrors it to the other:

```bash
export BASE_URL=http://127.0.0.1:8000/v1
export MODEL=qwen3-fastcontext
export API_KEY=local
```

or:

```bash
export FC_BASE_URL=http://127.0.0.1:8000/v1
export FC_MODEL=qwen3-fastcontext
export FC_API_KEY=local
```

Optional:

```bash
export FASTCONTEXT_MAX_TURNS=8
export FASTCONTEXT_TRAJ_DIR=/tmp/fastcontext-trajectories
```

Trajectories intentionally default outside the repository to avoid contaminating subsequent searches.

## Skill locations

- Codex: `~/.codex/skills/repo-locate`
- Claude Code: `~/.claude/skills/repo-locate`
- Antigravity CLI (`agy`): `~/.gemini/antigravity-cli/skills/repo-locate`

Run `bash ./install.sh` from the cloned skill directory to create symlinks for all three.

## MCP transport

If Codex or Claude Code already exposes a read-only FastContext MCP tool, the skill prefers it. No MCP configuration is embedded here because MCP registration is host-specific. The skill remains usable through the native CLI in any shell-capable agent.
