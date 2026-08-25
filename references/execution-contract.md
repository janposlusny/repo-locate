# Experimental execution contract

`repo-locate` uses a small local model as a prerequisite localization step. That exposed a gap between **skill semantics** (when a capability should be used) and **runtime semantics** (how the capability must execute).

This document records the portable semantics we currently need. It is an experiment, not an Agent Skills standard and not a host configuration format.

## Portable semantics

```yaml
execution:
  cwd: repository-root
  completion: required
  expected_duration_seconds: 120
  timeout_seconds: 180

coordination:
  while_running:
    redundant_repository_search: wait

fallback:
  backend_unavailable: host-search
  timeout: host-search
  insufficient_result: refine-once-then-host-search
```

### `cwd: repository-root`

Repository structure is part of FastContext's input. The locator must execute from the repository being explored, not from a host-agent scratch directory.

### `completion: required`

The locator result is evidence for the next reasoning step. The host should wait for completion rather than treating normal local-inference latency as permission to continue down an independent search path.

This is intentionally semantic rather than a field such as `foreground: true` or `WaitMsBeforeAsync`. Different hosts expose different execution controls.

### Expected duration and timeout

Local inference may commonly take tens of seconds to around two minutes on consumer hardware. `expected_duration_seconds` communicates that this latency is normal; `timeout_seconds` defines when fallback becomes reasonable.

These values are defaults for this skill, not universal recommendations for other skills.

### Coordination while running

Starting a broad host-agent repository search while FastContext is still computing defeats the purpose of delegation and can consume more frontier context than the locator saves. Wait for the first result unless the call has failed or timed out.

### Fallback

Backend failure and poor localization are different outcomes:

- **backend unavailable / timeout:** fall back immediately to host search;
- **insufficient localization:** make at most one focused refinement, then fall back;
- **successful localization:** verify returned regions narrowly and continue from them.

## Host mappings

A host is free to compile these semantics into its own controls. Examples of the intended mapping are:

| Portable semantic | Typical host mapping |
| --- | --- |
| `cwd: repository-root` | command/tool working-directory argument |
| `completion: required` | synchronous/foreground execution |
| `timeout_seconds: 180` | shell/tool timeout or foreground wait threshold |
| `redundant_repository_search: wait` | agent instruction/policy while the call is active |
| fallback rules | normal host repository tools |

Host-specific mappings belong in separate references rather than in the portable `SKILL.md` frontmatter.

## Why not MCP?

MCP can provide a clean tool boundary and may be a useful optional transport, but it moves process-lifecycle semantics behind a server rather than defining the missing execution contract. `repo-locate` keeps the shell wrapper as the canonical minimal path while we learn which runtime semantics are actually portable.

## Research status

The schema above is deliberately small. The goal is to collect evidence from multiple harnesses before deciding whether fields such as retries, streaming, preflight, resource requirements, or concurrency deserve first-class representation.
