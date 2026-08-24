from __future__ import annotations

from dataclasses import dataclass

from harvestbot.economics import ProductEvent, ValuationModel


@dataclass(frozen=True)
class Job:
    name: str
    events: tuple[ProductEvent, ...]
    estimated_value: float


@dataclass(frozen=True)
class BeamState:
    selected: tuple[Job, ...]
    approx_value: float


class Scheduler:
    def __init__(self, vm: ValuationModel) -> None:
        self.vm = vm

    def generate_problem(
        self,
        candidates: tuple[tuple[str, tuple[ProductEvent, ...]], ...],
        market_inv: dict[str, int],
        unlocked_shops: tuple[str, ...],
    ) -> tuple[Job, ...]:
        """Candidate admission deliberately uses known-current valuation."""
        jobs = []
        for name, events in candidates:
            estimated = self.vm.events_value(events, market_inv, unlocked_shops)
            if estimated > 0:
                jobs.append(Job(name=name, events=events, estimated_value=estimated))
        return tuple(jobs)

    def _approximate_value(
        self,
        selected: tuple[Job, ...],
        current_day: int,
        market_inv: dict[str, int],
        unlocked_shops: tuple[str, ...],
    ) -> float:
        """Approximate value used only for intermediate beam-state ranking."""
        events = tuple(event for job in selected for event in job.events)
        # Benchmark target: long-horizon beam ranking currently uses known-current
        # valuation here, even though the valuation model can represent future unlocks.
        value = self.vm.events_value(events, market_inv, unlocked_shops)
        diversity_bonus = 0.05 * len({event.product for event in events})
        return value + diversity_bonus

    @staticmethod
    def _state_rank(state: BeamState) -> tuple[float, int]:
        return (state.approx_value, -len(state.selected))

    def _prune(self, states: list[BeamState], width: int) -> list[BeamState]:
        return sorted(states, key=self._state_rank, reverse=True)[:width]

    def expand_beam(
        self,
        admitted_jobs: tuple[Job, ...],
        current_day: int,
        market_inv: dict[str, int],
        unlocked_shops: tuple[str, ...],
        width: int = 4,
    ) -> list[BeamState]:
        states = [
            BeamState(
                selected=(job,),
                approx_value=self._approximate_value(
                    (job,), current_day, market_inv, unlocked_shops
                ),
            )
            for job in admitted_jobs
        ]
        return self._prune(states, width)

    def evaluate_portfolio(
        self,
        jobs: tuple[Job, ...],
        market_inv: dict[str, int],
        unlocked_shops: tuple[str, ...],
    ) -> float:
        """Final portfolio comparison deliberately remains known-current."""
        events = tuple(event for job in jobs for event in job.events)
        return self.vm.events_value(events, market_inv, unlocked_shops)
