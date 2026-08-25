# Antigravity CLI runtime mapping

This is the Antigravity-specific mapping for the portable contract in [execution-contract.md](execution-contract.md).

Antigravity exposes the execution controls we need directly on `run_command`, but models do not reliably copy those controls from skill prose into each invocation. The preferred integration is therefore a tiny **PreToolUse execution compiler** that rewrites only repo-locate calls before execution.

## Portable contract -> Antigravity

```yaml
execution:
  cwd: repository-root
  completion: required
  expected_duration_seconds: 120
  timeout_seconds: 180
```

maps to the native `run_command` arguments:

```yaml
Cwd: <repository-root>
RunPersistent: false
WaitMsBeforeAsync: 180000
```

`WaitMsBeforeAsync` is a foreground-wait threshold, not a universal wall-clock timeout. The portable timeout remains a semantic fallback boundary until Antigravity exposes a matching per-call timeout control that can be mapped cleanly.

## Execution compiler

The experimental plugin lives at:

```text
integrations/antigravity/
├── plugin.json
├── hooks.json
└── hooks/
    └── compile_execution.py
```

Its `PreToolUse` hook matches `run_command`. For ordinary shell commands it passes through unchanged. For a command invoking `repo-locate.sh`, it preserves the model's command and arguments but overwrites the execution controls above.

This keeps the skill portable:

```text
SKILL.md / execution-contract.md
        portable semantics
                ↓
Antigravity PreToolUse hook
        host-specific compiler
                ↓
run_command(Cwd=repo, WaitMsBeforeAsync=180000, RunPersistent=false)
```

No lockfile or polling state machine is required when the compiler keeps the locator in the intended lifecycle.

## Why compile instead of instruct

A model can correctly activate the skill and still omit `Cwd`, `WaitMsBeforeAsync`, or `RunPersistent` from the resulting tool call. Once a 60–120 second locator is backgrounded, Antigravity may spend frontier-model turns polling tasks and logs or exploring the repository in parallel. That can erase the context savings from delegation.

The compiler makes execution semantics deterministic rather than relying on the model to reproduce host-specific arguments from prose.

## Expected trajectory

```text
repo-locate starts
  -> local inference runs in the repository root
  -> run_command waits for stdout
  -> repo-locate returns citations
  -> inspect cited regions narrowly
  -> reason / edit / test normally
```

It should not look like:

```text
repo-locate starts
  -> background task
  -> schedule wait
  -> poll task/log
  -> parallel grep/find
```

If the compiled synchronous path still produces redundant broad exploration *after* a successful localization result, treat that as a separate coordination-policy problem. Do not add a polling/search state machine preemptively.

## Hook compatibility note

Antigravity's current hook input uses `toolCall.name`, `toolCall.args`, and `workspacePaths`. The plugin relies on the CLI's pre-tool argument-overwrite capability. Validate the overwrite on the installed Antigravity version before using benchmark results; permission-review modes have had version-specific overwrite bugs. The current repo-locate benchmark uses `--dangerously-skip-permissions`, which avoids that permission-review interaction.

## Failure behavior

If the FastContext backend is unavailable, the command genuinely times out, or it returns invalid locations after one focused refinement, stop delegating and use Antigravity's normal repository tools.

Do not treat ordinary local-model latency as a failure by itself.
