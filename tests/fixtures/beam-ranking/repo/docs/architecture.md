# Planner architecture

Crop planning uses a bounded beam search. The public entry point in `harvestbot.agent` delegates candidate admission, beam expansion, pruning, and final portfolio scoring to the scheduler.

The economics layer supports both known-current demand and a future-shop-unlock model. Offline analysis compares these modes, but production callers choose which valuation semantics they need.

When changing ranking behavior, avoid broad changes to candidate admission or final portfolio evaluation unless the task explicitly requires them.
