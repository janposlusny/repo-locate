# FastContext Query Guide

Use this reference when the first localization query is difficult to phrase or when a first result needs one refinement.

## Core pattern

A strong query usually contains three parts:

1. **Behavior** — what the code does from the user's perspective.
2. **Role** — implementation, caller, ranking path, validation, configuration, persistence, etc.
3. **Neighborhood** — tests, direct callers, downstream consumer, or config that should be returned with it.

Template:

`Find where <behavior> is implemented in <role/path>, and locate <tests/direct callers/related config> relevant to that path.`

## Useful query shapes

### Locate implementation + tests

`Find the production code that computes <behavior>, and the tests that exercise that production path.`

### Trace direct callers

`Locate the definition of <symbol> and its direct production callers involved in <subsystem>. Distinguish callers from imports, docs, and tests.`

### Find a ranking/decision point

`Find where <candidate/object> is scored or ranked before <pruning/selection/dispatch>, and tests covering that decision path.`

### Trace a cross-layer flow

`Trace <request/event> from <entry point> through <service/model/storage>, returning the key implementation ranges at each layer.`

### Impact analysis before editing

`Find production consumers of <symbol/config/schema> whose behavior would change if <specific semantic property> changes, plus tests for those consumers.`

## Refinement after the first call

Use concrete names discovered in the first result. Ask for one missing thing, not the whole task again.

Examples:

- `You found ValuationModel.events_value. Now locate its direct production callers used specifically for crop beam-state ranking and pruning.`
- `You found the handler. Locate the service method it calls and tests that assert the failure behavior.`
- `You found planning.py. Locate the function that assigns BeamState.approx_value and the pruning/ranking code that consumes it.`

## Avoid

- Bare keywords: `webhooks`, `valuation`, `scheduler`.
- Asking FastContext to implement or choose the fix.
- Encoding a long speculative architecture into the query.
- Asking for exhaustive proof on the first call.
- Treating documentation mentions as equivalent to production call sites.
