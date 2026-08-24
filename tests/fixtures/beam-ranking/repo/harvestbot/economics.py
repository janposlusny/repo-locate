from __future__ import annotations

from dataclasses import dataclass

SHOP_UNLOCK_DAY = {"bakery": 3, "grocer": 6, "hotel": 9, "market": 12}
PRODUCT_SHOPS = {
    "MELON": (),
    "STRAWBERRY": ("bakery", "grocer", "hotel", "market"),
    "WHEAT": ("bakery", "market"),
}


@dataclass(frozen=True)
class ProductEvent:
    product: str
    quantity: int
    day_offset: int


def daily_town_drain(product: str, unlocked_shops: tuple[str, ...]) -> float:
    """Known-current demand from shops that are already unlocked."""
    return 2.0 * sum(shop in unlocked_shops for shop in PRODUCT_SHOPS.get(product, ()))


def expected_future_town_drain(
    product: str,
    unlocked_shops: tuple[str, ...],
    target_day: int,
    current_day: int,
) -> float:
    """Expected demand by a future absolute day, including shops unlocked meanwhile."""
    absolute_target_day = current_day + target_day
    visible = set(unlocked_shops)
    for shop in PRODUCT_SHOPS.get(product, ()):
        # A shop unlocking on day u contributes only after that boundary.
        if SHOP_UNLOCK_DAY[shop] < absolute_target_day:
            visible.add(shop)
    return daily_town_drain(product, tuple(visible))


class ValuationModel:
    def events_value(
        self,
        events: tuple[ProductEvent, ...],
        market_inv: dict[str, int],
        unlocked_shops: tuple[str, ...],
        *,
        model_future_unlocks: bool = False,
        current_day: int = 0,
    ) -> float:
        value = 0.0
        for event in events:
            if model_future_unlocks:
                drain = expected_future_town_drain(
                    event.product,
                    unlocked_shops,
                    event.day_offset,
                    current_day,
                )
            else:
                drain = daily_town_drain(event.product, unlocked_shops)
            scarcity = max(1.0, 100.0 / max(1, market_inv.get(event.product, 100)))
            value += event.quantity * (1.0 + drain) * scarcity
        return value
