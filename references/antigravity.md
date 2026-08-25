# Antigravity CLI runtime mapping

This is a host-specific mapping for the portable contract in [execution-contract.md](execution-contract.md). It is guidance for the agent, not native Antigravity configuration.

## Shell invocation

When using Antigravity's shell/run-command tool for `repo-locate`:

- run from the repository root;
- keep the locator synchronous/foreground until it returns;
- allow up to about 180 seconds for normal local inference;
- do not mark the locator as a persistent/background command;
- do not start `schedule`, task polling, log polling, or broad repository search merely because the locator is still computing.

If the current `run_command` tool exposes host controls equivalent to these concepts, map them as follows:

```yaml
Cwd: <repository-root>
RunPersistent: false
WaitMsBeforeAsync: 180000
```

Host versions may expose different argument names or omit some of them. Preserve the semantics rather than inventing unsupported tool arguments.

## Completion behavior

A successful trajectory should look like:

```text
repo-locate starts
  -> local inference runs
  -> repo-locate returns stdout
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

The latter can erase the context savings that motivated delegation.

## Failure behavior

If the FastContext backend is unavailable, the command genuinely times out, or it returns invalid locations after one focused refinement, stop delegating and use Antigravity's normal repository tools.

Do not treat ordinary 30–120 second local-model latency as a failure by itself.
