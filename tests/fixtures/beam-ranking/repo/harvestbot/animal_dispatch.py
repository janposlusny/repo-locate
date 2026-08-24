from harvestbot.economics import ProductEvent, ValuationModel


def value_animal_feed(events: tuple[ProductEvent, ...]) -> float:
    """Unrelated consumer of the valuation model."""
    return ValuationModel().events_value(events, {}, ("market",))
