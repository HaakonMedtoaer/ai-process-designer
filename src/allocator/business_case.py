"""Business-case range. Every number comes from the user; nothing is defaulted.

Per step, current cost = volume x minutes per item x hourly cost.
After the redesign, people still spend time on:
- items that fall back to a human (fallback share x full manual minutes)
- reviewing the rest, if the step has human review (review minutes per item)

The range comes from the low/high values the user gives for fallback share and
review minutes. Build and running costs (development, API usage) are NOT included.
"""

from dataclasses import dataclass, field

from .rules import Allocation, Role

EXCLUDED = "Excludes build and running costs (development time, API usage, maintenance)."


@dataclass(frozen=True)
class Range:
    low: float
    high: float

    def __post_init__(self):
        if self.low > self.high:
            raise ValueError(f"low ({self.low}) is above high ({self.high})")


@dataclass(frozen=True)
class StepInputs:
    name: str
    allocation: Allocation
    volume_per_month: float | None
    minutes_per_item: float | None
    fallback_share: Range | None = None  # 0..1, needed for AI call and agent steps
    review_minutes: Range | None = None  # needed when the step has human review
    fallback_share_verified: bool = False  # True only if measured, not assumed
    review_minutes_verified: bool = False


@dataclass
class StepResult:
    name: str
    current_cost: float | None
    saving: Range | None
    missing: list[str] = field(default_factory=list)
    unverified: list[str] = field(default_factory=list)


@dataclass
class CaseResult:
    steps: list[StepResult]
    total_saving: Range | None  # None if any step is missing inputs
    assumptions: list[str]

    def drivers(self) -> list[StepResult]:
        """Steps with a saving, largest high-end saving first."""
        with_saving = [s for s in self.steps if s.saving and s.saving.high > 0]
        return sorted(with_saving, key=lambda s: s.saving.high, reverse=True)


def _step(inp: StepInputs, hourly_cost: float) -> StepResult:
    role = inp.allocation.role
    missing = []
    if inp.volume_per_month is None:
        missing.append("volume_per_month")
    if inp.minutes_per_item is None:
        missing.append("minutes_per_item")
    automated = role in (Role.AI_CALL, Role.AGENT)
    if automated and inp.fallback_share is None:
        missing.append("fallback_share")
    if automated and inp.allocation.human_review and inp.review_minutes is None:
        missing.append("review_minutes")
    if role is None:
        missing.append("allocation")
    if missing:
        return StepResult(inp.name, None, None, missing=missing)

    if inp.fallback_share and not (0 <= inp.fallback_share.low and inp.fallback_share.high <= 1):
        raise ValueError(f"{inp.name}: fallback_share must be between 0 and 1")

    per_minute = hourly_cost / 60
    current = inp.volume_per_month * inp.minutes_per_item * per_minute

    if role is Role.HUMAN:
        return StepResult(inp.name, current, Range(0.0, 0.0))
    if role is Role.SCRIPT:
        return StepResult(inp.name, current, Range(current, current))

    unverified = []
    if not inp.fallback_share_verified:
        unverified.append("fallback_share")
    review = inp.review_minutes if inp.allocation.human_review else Range(0.0, 0.0)
    if inp.allocation.human_review and not inp.review_minutes_verified:
        unverified.append("review_minutes")

    def remaining(share: float, review_min: float) -> float:
        manual = share * inp.minutes_per_item
        reviewing = (1 - share) * review_min
        return inp.volume_per_month * (manual + reviewing) * per_minute

    worst = remaining(inp.fallback_share.high, review.high)
    best = remaining(inp.fallback_share.low, review.low)
    return StepResult(inp.name, current, Range(current - worst, current - best),
                      unverified=unverified)


def compute(steps: list[StepInputs], hourly_cost: float | None) -> CaseResult:
    if hourly_cost is None:
        results = [StepResult(s.name, None, None, missing=["hourly_cost"]) for s in steps]
        return CaseResult(results, None, [EXCLUDED])
    results = [_step(s, hourly_cost) for s in steps]
    complete = all(r.saving is not None for r in results)
    total = None
    if complete:
        total = Range(sum(r.saving.low for r in results), sum(r.saving.high for r in results))
    assumptions = [
        EXCLUDED,
        "Script steps are assumed to remove all manual time for that step.",
        "Human steps are assumed unchanged.",
        "Items that fall back to a human take the same time as today.",
    ]
    return CaseResult(results, total, assumptions)
