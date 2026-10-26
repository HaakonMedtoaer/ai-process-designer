# allocator (working name)

Takes a finance back-office process and assigns each step to a script, a single AI call,
an agent or a human. The default is the simplest option that works. An agent has to earn
its place.

Status: early. The allocation rules and business-case math exist and are tested.
There is no user interface or model integration yet.

- Rubric: [`docs/rubric-draft.md`](docs/rubric-draft.md)
- Test cases and baselines: [`cases/`](cases/)
- Rules: `src/allocator/rules.py`. Business case: `src/allocator/business_case.py`

## Run the tests

```
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
```
