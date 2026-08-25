---
name: repo-locate
description: Locate production code, tests, callers, dependencies, and configuration in an unfamiliar repository using FastContext. Use before broad repository exploration, cross-file tracing, debugging unfamiliar behavior, impact analysis, or when asked where code lives. Skip when the exact target files or ranges are already known.
metadata:
  version: "0.2.0"
  backend: "fastcontext"
---

# Repo Locate

Use FastContext as a **read-only localization specialist**. Its job is to find the smallest useful set of repository locations for the current task. The outer agent remains responsible for understanding the code, deciding the change, editing, and testing.

## When to use

Use this skill when any of these are true:

- You are cold-starting in an unfamiliar part of a repository.
- The task likely crosses files, layers, callers, dependencies, or tests.
- You would otherwise start with broad `grep`, `find`, or repeated file reads.
- You need to locate where a behavior is implemented, scored, validated, configured, or tested.
- You need impact context before changing code.

Skip it when the exact relevant file/symbol/range is already known, or the answer is confined to 2–3 files already inspected in the current turn.

## Execution contract

The locator is a local inference step, not a background job. Its result is a prerequisite for the next repository-exploration step.

- Run from the repository root.
- **Completion is required:** wait for the locator's completed stdout before continuing.
- A normal local run may take roughly 30–120 seconds. Do not interpret ordinary locator latency as failure.
- Allow up to 180 seconds before treating the invocation as timed out unless the host has a stricter user-configured limit.
- Do not start redundant broad repository searches while the locator is still running.
- If the backend is unavailable or the locator genuinely times out, fall back to the host agent's normal repository search.
- If the result is insufficient, refine once, then fall back.

These are portable semantics, not a host-specific tool schema. Hosts may map them to different runtime controls. See [references/execution-contract.md](references/execution-contract.md). Under Antigravity CLI, also read [references/antigravity.md](references/antigravity.md) before invoking the shell wrapper.

## Procedure

1. **Form a localization query, not a solution prompt.** Describe the behavior or flow to locate and, when useful, ask for its tests or direct callers. Do not ask FastContext to design or implement the fix.
2. **Delegate once.** Resolve this skill directory and run:

   `bash scripts/repo-locate.sh "<focused localization query>"`

   If the host has an intentionally configured equivalent FastContext tool, it may use that instead, but preserve the execution contract above.
3. **Wait for the completed result.** Do not background the locator merely because local inference is slow, and do not begin an alternative repository search in parallel.
4. **Treat returned citations as candidate evidence.** Open the cited ranges yourself, normally with about 30–80 lines of surrounding context. Verify that the symbols actually implement the requested behavior.
5. **Do not immediately repeat broad repository searches.** If the citations are sufficient, continue from them.
6. **If evidence is incomplete, make one refined FastContext query.** Pivot using concrete names learned from the first result, or ask explicitly for a missing layer, caller, test, or configuration path.
7. **Fall back to normal repository search only after that.** Use the outer agent's own search tools if FastContext returns invalid citations, misses the target after refinement, the backend is unavailable, the call genuinely times out, or the task requires exhaustive proof.
8. **Solve with the outer agent.** Reason about the code, edit, test, and review normally. FastContext does not get authority over the implementation.

## Query rules

Prefer queries that name **behavior + role + requested neighborhood**.

Good:

- `Find where crop candidates receive approximate values used for beam-state ranking and pruning, and the tests covering that ranking path.`
- `Find where incoming webhook payloads are validated, where HMAC signatures are checked, and the tests for invalid signatures.`
- `Trace the direct production callers of ValuationModel.events_value that participate in crop planning, and locate tests for those callers.`

Weak:

- `crop valuation`
- `how does the backend work`
- `fix the beam search`

Do not overload the first query with a full proposed patch. FastContext should locate the code; the outer agent should infer the change.

For more patterns, read [references/query-guide.md](references/query-guide.md).

## Evidence discipline

- A path or symbol is not trusted until the outer agent reads it.
- A textual mention is not necessarily a call site.
- Prefer production implementation and its tests over docs or analysis scripts unless the task explicitly concerns those artifacts.
- If FastContext gives a plausible explanation but the citations do not support it, trust the code you verified, not the explanation.
- Never edit based only on an unverified FastContext citation.

## Efficiency contract

FastContext is useful only if it reduces outer-agent exploration. After a successful call:

- Read cited regions narrowly.
- Avoid duplicate repo-wide grep/find for the same question.
- Refine FastContext at most once before falling back.
- Keep FastContext trajectories outside the target repository.
