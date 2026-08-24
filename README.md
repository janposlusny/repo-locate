# repo-locate

A portable Agent Skill that delegates cold-start repository localization to FastContext while keeping reasoning, editing, and verification in the outer coding agent.

The same skill directory is designed for Codex, Claude Code, and Antigravity CLI (`agy`).

## Install

1. Put this directory somewhere permanent.
2. Run `./install.sh` to symlink it into all three agents.
3. Ensure `fastcontext` is on `PATH` and your local FastContext endpoint variables are configured, or register a FastContext MCP tool in the host agent.

See `references/setup.md` for details.
