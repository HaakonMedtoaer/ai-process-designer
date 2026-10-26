# allocator (working name)

Takes a finance back-office process and assigns each step to a script, a single AI call,
an agent or a human. The default is the simplest option that works. An agent has to earn
its place.

Status: early. Runs locally. Not yet evaluated against the test cases.

How it works: a model splits the process text into steps and proposes five scores per step,
each with a reason and a quote. You set volume and can change any score. Plain code then
applies the allocation rules, so the model never picks the role. The business case uses
only numbers you enter.

- Rubric: [`docs/rubric-draft.md`](docs/rubric-draft.md)
- Test cases and baselines: [`cases/`](cases/)
- Rules: `src/allocator/rules.py`. Business case: `src/allocator/business_case.py`

## Run it locally

You need Python 3.11+ and an Anthropic API key.

```
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
export ANTHROPIC_API_KEY=...        # never commit this
.venv/bin/streamlit run app.py
```

Each analysis is one model call (default model `claude-opus-5-5`, change with `ALLOCATOR_MODEL`).
Save an analysis to `results/` and you can reload it later without a key or any cost.

## Run the tests

```
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
```
