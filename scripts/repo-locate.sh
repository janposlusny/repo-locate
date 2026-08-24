#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo 'usage: repo-locate.sh "<focused localization query>"' >&2
  exit 2
fi

if ! command -v fastcontext >/dev/null 2>&1; then
  echo 'repo-locate: fastcontext CLI is not on PATH' >&2
  echo 'Install/configure FastContext first, then retry.' >&2
  exit 127
fi

query="$*"

# Work from the repository root when possible. FastContext's native harness
# receives the repository structure from this working directory.
if repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  repo_root="$(pwd -P)"
fi

# Different maintained FastContext variants have used both prefixed and
# unprefixed OpenAI-compatible endpoint variables. Mirror either spelling so
# the wrapper remains usable across them without storing credentials here.
[[ -n "${BASE_URL:-}" && -z "${FC_BASE_URL:-}" ]] && export FC_BASE_URL="$BASE_URL"
[[ -n "${FC_BASE_URL:-}" && -z "${BASE_URL:-}" ]] && export BASE_URL="$FC_BASE_URL"
[[ -n "${MODEL:-}" && -z "${FC_MODEL:-}" ]] && export FC_MODEL="$MODEL"
[[ -n "${FC_MODEL:-}" && -z "${MODEL:-}" ]] && export MODEL="$FC_MODEL"
[[ -n "${API_KEY:-}" && -z "${FC_API_KEY:-}" ]] && export FC_API_KEY="$API_KEY"
[[ -n "${FC_API_KEY:-}" && -z "${API_KEY:-}" ]] && export API_KEY="$FC_API_KEY"

max_turns="${FASTCONTEXT_MAX_TURNS:-8}"
traj_dir="${FASTCONTEXT_TRAJ_DIR:-${TMPDIR:-/tmp}/fastcontext-trajectories}"
mkdir -p "$traj_dir"

repo_name="$(basename "$repo_root")"
stamp="$(date +%Y%m%d-%H%M%S)"
traj="$traj_dir/${repo_name}-${stamp}-$$.jsonl"

cd "$repo_root"
exec fastcontext \
  --query "$query" \
  --max-turns "$max_turns" \
  --traj "$traj" \
  --citation
