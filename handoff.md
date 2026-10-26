# Handoff

## Current state
- Files: `docs/rubric-draft.md` (rubric, agreed in principle), `cases/` (5 cases + blank baselines).
- No code yet. By agreement, rubric and test-case baselines come before code.
- Decided: niche = finance back-office. No deadlines; when-available project.

## Next steps (first-session agenda)
1. Haakon fills `cases/*/baseline.md` before the tool runs (Claude Code must not draft these).
2. Sparring partner (finance) reviews some baselines.
3. Decide whether to split variability into "messy input" and "unpredictable path", after baselines.
4. Then scaffold v0.1 (proposed: Python).

## Open questions
- Repo rename to fit the niche (Haakon does this in GitHub settings).
- Baseline quality: Haakon is not a finance specialist. Consider one finance reviewer for a subset.
- Rule-based vs LLM split: LLM scores, code allocates. Agreed as plan, unproven.
- Hosting: public demo with rate limit vs recording + repo.
- Name.

## Later features (not in v0.1)
- Tool proposes new steps, not just roles: invoice firewall (filter incoming invoices before AP:
  unknown supplier, duplicate, missing PO, fraud signals), invoice enrichment (fill cost centre/coding).
- Per-item fallback routing (see rubric proposal). Decide if it goes into v0.1 rubric.

## Gotchas
- Repo is meant to be public: no employer names, processes or data, and no personal
  job-search notes. The full project brief stays out of the repo for that reason.
- No invented numbers anywhere, including docs and examples.
- Case sources were found via search only; sandbox network blocks those sites. Open and confirm before citing.
- Case 01 overlaps the worked example Claude Code gave in chat (steps 2, 4, 5, 7). Its baseline is not blind.
