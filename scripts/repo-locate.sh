#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo 'usage: repo-locate.sh "<focused localization query>"' >&2
  exit 2
fi

fc_bin="$(command -v fastcontext || true)"
if [[ -z "$fc_bin" ]]; then
  echo 'repo-locate: fastcontext CLI is not on PATH' >&2
  echo 'Install/configure FastContext first, then retry.' >&2
  exit 127
fi

query="$*"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
launcher="$script_dir/run-fastcontext.py"

# Use the Python interpreter belonging to the installed FastContext console
# script. This keeps repo-locate compatible with `uv tool install`, where the
# fastcontext package lives in an isolated environment and is not importable by
# the user's normal python3.
shebang="$(head -n 1 "$fc_bin")"
fc_python=""
if [[ "$shebang" == '#!'* ]]; then
  interpreter="${shebang#\#!}"
  if [[ "$interpreter" == '/usr/bin/env '* ]]; then
    interpreter_name="${interpreter#/usr/bin/env }"
    fc_python="$(command -v "$interpreter_name" || true)"
  else
    fc_python="${interpreter%% *}"
  fi
fi

if [[ -z "$fc_python" || ! -x "$fc_python" ]]; then
  echo "repo-locate: could not resolve FastContext's Python interpreter from $fc_bin" >&2
  exit 126
fi

# Work from repository root when possible. FastContext's native harness
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

# The upstream CLI currently hardcodes the LLM default temperature at 1.0 and
# exposes no sampling flag. The bundled launcher sets 0.6 unless overridden.
export FASTCONTEXT_TEMPERATURE="${FASTCONTEXT_TEMPERATURE:-0.6}"

max_turns="${FASTCONTEXT_MAX_TURNS:-8}"
traj_dir="${FASTCONTEXT_TRAJ_DIR:-${TMPDIR:-/tmp}/fastcontext-trajectories}"
mkdir -p "$traj_dir"

repo_name="$(basename "$repo_root")"
stamp="$(date +%Y%m%d-%H%M%S)"
traj="$traj_dir/${repo_name}-${stamp}-$$.jsonl"

cd "$repo_root"
exec "$fc_python" "$launcher" \
  --query "$query" \
  --max-turns "$max_turns" \
  --traj "$traj" \
  --citation
