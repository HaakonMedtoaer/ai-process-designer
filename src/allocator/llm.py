"""Model call: split process text into steps and propose scores with evidence.

The model never picks a role. It proposes scores for five criteria, each with a
reason and a quote. Volume is left to the user. The rules in rules.py allocate.
"""

import os
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

MODEL = os.environ.get("ALLOCATOR_MODEL", "claude-opus-5-5")

ScoreValue = Literal["1", "2", "3", "unknown"]


class CriterionScore(BaseModel):
    score: ScoreValue
    reason: str = Field(description="One sentence. Why this score.")
    quote: str = Field(description="Exact words from the process text that support it, or empty.")


class ScoredStep(BaseModel):
    number: int
    name: str = Field(description="Short name, max 8 words.")
    description: str
    variability: CriterionScore
    error_cost: CriterionScore
    verifiability: CriterionScore
    accountability: CriterionScore
    access_risk: CriterionScore


class Analysis(BaseModel):
    steps: list[ScoredStep]
    open_questions: list[str] = Field(
        description="Information missing from the text that would change a score.")


SYSTEM = """You analyse finance back-office processes for an allocation tool.
Split the process into steps and score each step on five criteria.
You do not decide who or what performs a step. Code does that from your scores.

Steps:
- If the text has numbered steps, keep exactly that numbering and split.
- Otherwise, one step per distinct action with its own input and output.

Scores (use "unknown" when the text does not give enough to decide; never guess):
- variability: 1 = fixed format, structured fields. 2 = messy text or documents, but the
  step does one transformation. 3 = the number or order of actions depends on what is found.
- error_cost: 1 = cheap to catch and undo. 2 = costly but reversible.
  3 = irreversible, or harms a customer, money or legal position.
- verifiability: 1 = a rule can check the output. 2 = a person can check it quickly.
  3 = hard to check without redoing the work.
- accountability: 1 = nobody needs to own it. 2 = someone signs off, delegation is normal.
  3 = a named person must own the decision (law, policy, relationship).
- access_risk: 1 = no sensitive data or system access. 2 = reads sensitive data.
  3 = write access, payments, or broad system rights.

For every score give a one-sentence reason and an exact quote from the text when one exists.
Do not score volume; the user supplies it.
List open questions where missing information blocks or weakens a score."""


class AnalysisError(RuntimeError):
    pass


def analyse(process_text: str, client: anthropic.Anthropic | None = None) -> Analysis:
    client = client or anthropic.Anthropic()
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "medium"},
        output_format=Analysis,
        system=SYSTEM,
        messages=[{"role": "user", "content": process_text}],
    )
    if response.stop_reason == "refusal":
        raise AnalysisError("The model declined this request.")
    if response.stop_reason == "max_tokens":
        raise AnalysisError("The answer was cut off (max_tokens). Try a shorter process.")
    if response.parsed_output is None:
        raise AnalysisError("The model returned no usable analysis.")
    return response.parsed_output
