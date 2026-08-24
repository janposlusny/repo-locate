from harvestbot.economics import ProductEvent, ValuationModel, expected_future_town_drain


def test_future_drain_respects_absolute_unlock_boundary() -> None:
    before = expected_future_town_drain("STRAWBERRY", (), target_day=6, current_day=0)
    after = expected_future_town_drain("STRAWBERRY", (), target_day=7, current_day=0)
    assert after >= before


def test_events_value_defaults_to_known_current_behavior() -> None:
    vm = ValuationModel()
    events = (ProductEvent("STRAWBERRY", 10, 12),)
    known = vm.events_value(events, {"STRAWBERRY": 100}, ())
    explicit = vm.events_value(
        events,
        {"STRAWBERRY": 100},
        (),
        model_future_unlocks=False,
        current_day=4,
    )
    assert explicit == known
