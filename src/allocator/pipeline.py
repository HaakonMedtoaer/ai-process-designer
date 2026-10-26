"""Glue between the model's analysis, user input, the rules and the outputs."""

import json
from dataclasses import dataclass
from pathlib import Path

from .llm import Analysis, ScoredStep
from .rules import CRITERIA, RULE_TEXT, Allocation, Role, Scores, allocate

MODEL_CRITERIA = [c for c in CRITERIA if c != "volume"]


def _to_int(value: str) -> int | None:
    return None if value == "unknown" else int(value)


@dataclass
class StepResult:
    step: ScoredStep
    scores: Scores
    allocation: Allocation


def allocate_steps(analysis: Analysis, volume: dict[int, int | None],
                   overrides: dict[int, dict[str, int | None]] | None = None) -> list[StepResult]:
    """volume: user-supplied volume score per step number (None = not given).
    overrides: user corrections to model scores, per step number."""
    overrides = overrides or {}
    results = []
    for step in analysis.steps:
        values = {c: _to_int(getattr(step, c).score) for c in MODEL_CRITERIA}
        values["volume"] = volume.get(step.number)
        values.update(overrides.get(step.number, {}))
        scores = Scores(**values)
        results.append(StepResult(step, scores, allocate(scores)))
    return results


def label(a: Allocation) -> str:
    if a.needs_input:
        return "Needs input"
    text = a.role.value
    if a.human_review:
        text += " + review"
    return text


def explain(a: Allocation) -> list[str]:
    lines = [f"{rule}: {RULE_TEXT[rule]}" for rule in a.fired]
    if a.missing:
        lines.append("Missing: " + ", ".join(a.missing))
    return lines


def mermaid(results: list[StepResult]) -> str:
    """Left-to-right flow, one node per step, styled by role."""
    out = ["flowchart LR"]
    for r in results:
        n = r.step.number
        name = r.step.name.replace('"', "'")
        out.append(f'  S{n}["{n}. {name}<br/><i>{label(r.allocation)}</i>"]')
        if r.allocation.fallback:
            out.append(f'  S{n} -. "unsure items" .-> H{n}(["Human"])')
        role = r.allocation.role.value if r.allocation.role else "Needs input"
        out.append(f"  class S{n} {_css(role)}")
    for a, b in zip(results, results[1:]):
        out.append(f"  S{a.step.number} --> S{b.step.number}")
    out += [
        "  classDef script fill:#dbeafe,stroke:#1d4ed8",
        "  classDef ai fill:#ede9fe,stroke:#6d28d9",
        "  classDef agent fill:#fef3c7,stroke:#b45309",
        "  classDef human fill:#dcfce7,stroke:#15803d",
        "  classDef unknown fill:#fee2e2,stroke:#b91c1c",
    ]
    return "\n".join(out)


def _css(role: str) -> str:
    return {Role.SCRIPT.value: "script", Role.AI_CALL.value: "ai",
            Role.AGENT.value: "agent", Role.HUMAN.value: "human"}.get(role, "unknown")


def risks(results: list[StepResult], analysis: Analysis) -> list[str]:
    out = []
    for r in results:
        a, n = r.allocation, r.step.number
        if a.needs_input:
            out.append(f"Step {n}: not allocated. Missing {', '.join(a.missing)}.")
        if a.role is Role.AGENT:
            out.append(f"Step {n}: agent. Test it on real cases first and log every action it takes.")
        if a.fallback:
            out.append(f"Step {n}: saving depends on how many items fall back to a human. Measure it.")
    out += [f"Open question: {q}" for q in analysis.open_questions]
    return out


def save(analysis: Analysis, path: Path) -> None:
    path.write_text(analysis.model_dump_json(indent=2))


def load(path: Path) -> Analysis:
    return Analysis.model_validate(json.loads(path.read_text()))
