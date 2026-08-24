from harvestbot.economics import ProductEvent, ValuationModel
from harvestbot.planning import BeamState, Job, Scheduler


def test_prune_keeps_highest_approximate_value() -> None:
    scheduler = Scheduler(ValuationModel())
    melon = Job("melon", (ProductEvent("MELON", 20, 18),), 10.0)
    strawberry = Job("strawberry", (ProductEvent("STRAWBERRY", 20, 18),), 9.0)
    states = [
        BeamState((melon,), 10.0),
        BeamState((strawberry,), 9.0),
    ]
    survivor = scheduler._prune(states, width=1)
    assert survivor[0].selected[0].name == "melon"


def test_generate_problem_uses_estimated_value_for_admission() -> None:
    scheduler = Scheduler(ValuationModel())
    candidates = (("wheat", (ProductEvent("WHEAT", 5, 2),)),)
    jobs = scheduler.generate_problem(candidates, {"WHEAT": 100}, ("bakery",))
    assert jobs and jobs[0].estimated_value > 0


def test_final_portfolio_is_separate_from_beam_rank() -> None:
    scheduler = Scheduler(ValuationModel())
    job = Job("wheat", (ProductEvent("WHEAT", 5, 2),), 1.0)
    value = scheduler.evaluate_portfolio((job,), {"WHEAT": 100}, ("bakery",))
    assert value > 0
