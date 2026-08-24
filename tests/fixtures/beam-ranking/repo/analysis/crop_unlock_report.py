from harvestbot.economics import ProductEvent, ValuationModel


def compare_known_vs_future() -> tuple[float, float]:
    """Offline ablation; not part of production beam search."""
    vm = ValuationModel()
    events = (ProductEvent("STRAWBERRY", 20, 18),)
    known = vm.events_value(events, {"STRAWBERRY": 100}, ())
    future = vm.events_value(
        events,
        {"STRAWBERRY": 100},
        (),
        model_future_unlocks=True,
        current_day=4,
    )
    return known, future
