from __future__ import annotations

from harvestbot.economics import ProductEvent, ValuationModel
from harvestbot.planning import Scheduler


def choose_crop_plan(current_day: int) -> str:
    """Entry point for one crop-planning pass."""
    scheduler = Scheduler(ValuationModel())
    candidates = (
        ("melon", (ProductEvent("MELON", 20, 18),)),
        ("strawberry", (ProductEvent("STRAWBERRY", 20, 18),)),
    )
    jobs = scheduler.generate_problem(candidates, {"MELON": 100, "STRAWBERRY": 100}, ())
    # The scheduler owns beam expansion, ranking, pruning, and final portfolio evaluation.
    beam = scheduler.expand_beam(jobs, current_day, {"MELON": 100, "STRAWBERRY": 100}, ())
    return beam[0].selected[0].name
