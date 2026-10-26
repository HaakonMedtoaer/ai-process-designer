# Allocation rubric (DRAFT v0, for Haakon to edit)

Status: proposal from Claude Code. Nothing here is decided until Haakon signs off.
Change it freely on paper first; code follows the rubric, not the other way round.

## Roles (the ladder)

1. **Script/rule**: deterministic code or a configured rule.
2. **Single AI call**: one model call with a fixed prompt, fixed output schema.
3. **Agent**: a model that chooses its own next action (tools, number of steps).
4. **Human**: a named person does or owns the step.

Separate from the role: a **human review** flag can sit on any AI or agent step.

## Scale

Each criterion gets `1`, `2`, `3`, or `unknown`. Every score carries a one-line
reason and, where possible, a quote from the user's process text.
`unknown` is a real value. It blocks allocation for that step and the tool asks
the user instead of guessing.

| Criterion | 1 | 2 | 3 |
|---|---|---|---|
| Input variability (V) | Fixed format, structured fields | Messy text, but the step does one transformation | Path depends on content: the number or order of actions is not known in advance |
| Error cost (E) | Cheap to catch and undo | Costly but reversible | Irreversible, or harms a customer, money or legal position |
| Verifiability (C) | A rule can check the output | A person can check it in under ~2 minutes | Hard to check without redoing the work |
| Accountability (A) | Nobody needs to own it | Someone signs off, but delegation is normal | A named person must own the decision (law, policy, relationship) |
| Access and risk (R) | No sensitive data or system access | Read access to sensitive data | Write access, payments, or broad system rights |
| Volume (Q) | Rare (user-supplied threshold) | Moderate | High |

Volume comes from the user's numbers. The tool never estimates it.

## Mapping rules (applied in order, first match wins)

Gates:

- **G0 Unknown**: any criterion `unknown` -> no allocation, ask the user.
- **G1 Accountability**: A=3 -> Human owns the decision. AI may prepare inputs (shown as a separate prep step).
- **G2 Not worth it**: Q=1 and V>=2 -> Human (automation not justified at this volume). Q=1 and V=1 -> Script only if trivially cheap, else Human. *(Open: what counts as "trivially cheap"?)*
- **G3 Risky and unverifiable**: R=3 and C=3 -> Human.

Ladder (take the lowest rung that fits):

- **L1**: V=1 -> Script/rule.
- **L2**: V=2 -> Single AI call.
- **L3**: V=3 and C<=2 -> Agent.
- **L4**: V=3 and C=3 -> Human (an agent whose output cannot be checked is not justified).

Review overlay (after the role is set, AI and agent steps only):

- **H1**: E>=2 and C>=2 -> add human review.
- **H2**: R>=2 on an agent step -> add human review.
- **H3**: E=3 on an agent step -> human review, always.

## Who decides what (proposed answer to the open design question)

- **LLM**: splits text into steps, proposes the six scores with reasons and quotes, writes the explanations.
- **Code**: the gates, ladder and overlay above. Deterministic, unit-tested.
- **User**: can override any score in the results view and see the allocation change.

So the model never picks the role directly. It can be wrong about a score, and
that error is visible and correctable. Whether this split holds up is something
the test set should tell us.

## Known weak spots in this draft

- V merges two things (input messiness and path unpredictability). May need splitting.
- The 1/2/3 anchors for E and R are judgement calls. Test cases will show where they blur.
- "Under ~2 minutes" for C=2 is an arbitrary number picked as a starting point, not evidence.
- No rule yet for steps that are really several steps glued together.

## Proposal from baseline round 1: per-item fallback

Haakon's baselines use a pattern the rubric above cannot express: an AI call handles
most items, and items it is unsure about go to a human. That is routing per item,
not one role per step.

Proposed addition: a step can have a **primary role** and a **fallback role** with a
**routing condition**. Example: primary = AI call, fallback = Human, condition =
"extraction fails a rule check or confidence is below threshold".

- The routing condition should prefer rule checks (totals add up, VAT is correct,
  PO number exists, supplier is known) over the model's own confidence score.
- The share of items that falls back is a user-supplied assumption. The business case
  must show it as an input and flag it, because the saving depends heavily on it.
