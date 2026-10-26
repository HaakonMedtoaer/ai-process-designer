# Handoff

## Current state
- Files: `docs/rubric-draft.md` (rubric v0.1), `cases/` (5 cases, partial baselines),
  `src/allocator/` (rules + business case, no model calls), `tests/` (27 passing).
- No code yet. By agreement, rubric and test-case baselines come before code.
- Decided: niche = finance back-office. No deadlines; when-available project.

## Next steps (first-session agenda)
1. Haakon settles hosting (see open questions). Then: LLM step extraction + scoring, then UI.
2. Haakon fills `cases/*/baseline.md` before the tool runs (Claude Code must not draft these).
3. Sparring partner (finance) reviews some baselines.
4. Decide whether to split variability into "messy input" and "unpredictable path".

## Open questions
- Repo rename to fit the niche (Haakon does this in GitHub settings).
- Baseline quality: Haakon is not a finance specialist. Consider one finance reviewer for a subset.
- Rule-based vs LLM split: LLM scores, code allocates. Agreed as plan, unproven.
- Hosting: GitHub Pages is static only (no Python server, no secret API key). Options pending.
- Name.

## Later features (not in v0.1)
- Tool proposes new steps, not just roles: invoice firewall (filter incoming invoices before AP:
  unknown supplier, duplicate, missing PO, fraud signals), invoice enrichment (fill cost centre/coding).

## Gotchas
- Run tests: `.venv/bin/pip install -e ".[dev]"` then `.venv/bin/pytest`.
- Repo is meant to be public: no employer names, processes or data, and no personal
  job-search notes. The full project brief stays out of the repo for that reason.
- No invented numbers anywhere, including docs and examples.
- Case sources were found via search only; sandbox network blocks those sites. Open and confirm before citing.
- Case 01 overlaps the worked example Claude Code gave in chat (steps 2, 4, 5, 7). Its baseline is not blind.
