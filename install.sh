#!/usr/bin/env bash
set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

targets=(
  "$HOME/.codex/skills/repo-locate"
  "$HOME/.claude/skills/repo-locate"
  "$HOME/.gemini/antigravity-cli/skills/repo-locate"
)

for target in "${targets[@]}"; do
  mkdir -p "$(dirname "$target")"
  if [[ -e "$target" && ! -L "$target" ]]; then
    echo "skip: $target exists and is not a symlink" >&2
    continue
  fi
  ln -sfn "$src" "$target"
  echo "linked: $target -> $src"
done

echo 'Restart/reload each coding agent if the skill is not discovered immediately.'
