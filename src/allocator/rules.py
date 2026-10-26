"""Allocation rules from docs/rubric-draft.md.

Scores are 1, 2, 3, or None (unknown). The rules are applied in a fixed order and
every rule that fires is recorded, so the result can be explained step by step.
"""

from dataclasses import dataclass, field
from enum import Enum

CRITERIA = (
    "variability",     # V
    "error_cost",      # E
    "verifiability",   # C
    "accountability",  # A
    "access_risk",     # R
    "volume",          # Q
)


class Role(str, Enum):
    SCRIPT = "Script"
    AI_CALL = "AI call"
    AGENT = "Agent"
    HUMAN = "Human"


@dataclass(frozen=True)
class Scores:
    variability: int | None
    error_cost: int | None
    verifiability: int | None
    accountability: int | None
    access_risk: int | None
    volume: int | None

    def __post_init__(self):
        for name in CRITERIA:
            value = getattr(self, name)
            if value is not None and value not in (1, 2, 3):
                raise ValueError(f"{name} must be 1, 2, 3 or None, got {value!r}")

    def unknown(self) -> list[str]:
        return [name for name in CRITERIA if getattr(self, name) is None]


@dataclass
class Allocation:
    role: Role | None  # None means the step could not be allocated
    human_review: bool = False
    fallback: Role | None = None  # role that handles items the primary role flags
    fired: list[str] = field(default_factory=list)  # rule ids, in order
    missing: list[str] = field(default_factory=list)  # criteria that blocked allocation

    @property
    def needs_input(self) -> bool:
        return self.role is None


def allocate(s: Scores) -> Allocation:
    # G0: never guess. Unknown scores block allocation.
    missing = s.unknown()
    if missing:
        return Allocation(role=None, fired=["G0"], missing=missing)

    # Gates
    if s.accountability == 3:
        return Allocation(role=Role.HUMAN, fired=["G1"])
    if s.volume == 1:
        return Allocation(role=Role.HUMAN, fired=["G2"])
    if s.access_risk == 3 and s.verifiability == 3:
        return Allocation(role=Role.HUMAN, fired=["G3"])

    # Ladder: lowest rung that fits
    if s.variability == 1:
        return Allocation(role=Role.SCRIPT, fired=["L1"])
    if s.variability == 2:
        result = Allocation(role=Role.AI_CALL, fired=["L2"])
    elif s.verifiability <= 2:
        result = Allocation(role=Role.AGENT, fired=["L3"])
    else:
        return Allocation(role=Role.HUMAN, fired=["L4"])

    # Review overlay (AI call and agent only)
    if s.error_cost >= 2 and s.verifiability >= 2:
        result.human_review = True
        result.fired.append("H1")
    if result.role is Role.AGENT and s.access_risk >= 2:
        result.human_review = True
        result.fired.append("H2")
    if result.role is Role.AGENT and s.error_cost == 3:
        result.human_review = True
        result.fired.append("H3")

    # Per-item fallback: items the model is unsure about go to a person
    result.fallback = Role.HUMAN
    result.fired.append("F1")
    return result


RULE_TEXT = {
    "G0": "One or more scores are unknown. Not allocated; ask the user.",
    "G1": "A named person must own this decision.",
    "G2": "Volume is too low to justify automation.",
    "G3": "High-risk access and output that cannot be checked.",
    "L1": "Fixed-format input: a script or rule is enough.",
    "L2": "Messy input, one transformation: a single AI call is enough.",
    "L3": "Unpredictable path and checkable output: an agent is justified.",
    "L4": "Unpredictable path but output cannot be checked: keep a human.",
    "H1": "Mistakes are costly and not rule-checkable: a human reviews the output.",
    "H2": "Agent needs sensitive access: a human reviews the output.",
    "H3": "Agent mistakes would be irreversible: a human always reviews.",
    "F1": "Items that fail checks or are low-confidence go to a human.",
}
