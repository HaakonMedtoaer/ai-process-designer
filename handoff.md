# Handoff

## Current state
- v0.1 skeleton runs locally: `streamlit run app.py`. Hosting decided: repo + local demo/recording.
- `src/allocator/`: rules, business case, llm (one structured-output call), pipeline (glue,
  Mermaid, risks). `tests/`: 37 passing, model call tested with a fake client only.
- NOT yet verified: a real model call (no API key in the build sandbox), Mermaid rendering
  (CDN blocked in sandbox), business-case table wiring in the UI (math itself is tested).
- Decided: niche = finance back-office. No deadlines; when-available project.

## Next steps
1. Haakon runs the app locally with his key on one case; report errors back.
2. Haakon fills `cases/*/baseline.md` before the tool runs (Claude Code must not draft these).
3. Sparring partner (finance) reviews some baselines.
4. Decide whether to split variability into "messy input" and "unpredictable path".

## Open questions
- Repo rename to fit the niche (Haakon does this in GitHub settings).
- Baseline quality: Haakon is not a finance specialist. Consider one finance reviewer for a subset.
- Rule-based vs LLM split: LLM scores, code allocates. Built, not yet evaluated.
- Name.

## Later features (not in v0.1)
- Tool proposes new steps, not just roles: invoice firewall (filter incoming invoices before AP:
  unknown supplier, duplicate, missing PO, fraud signals), invoice enrichment (fill cost centre/coding).

## Gotchas
- Model call uses beta server-side fallback (`fallbacks=default`) and effort `medium`.
- Commits: Claude Code commits on its own at each real, working change. Small, honest messages.
  No backdating, no artificial splitting. Tests must pass before each commit.
- Branches: `main` is the public default. Work happens on a session branch; merge to main
  at working milestones, after Haakon says ok.
- Run tests: `.venv/bin/pip install -e ".[dev]"` then `.venv/bin/pytest`.
- Repo is meant to be public: no employer names, processes or data, and no personal
  job-search notes. The full project brief stays out of the repo for that reason.
- No invented numbers anywhere, including docs and examples.
- Case sources were found via search only; sandbox network blocks those sites. Open and confirm before citing.
- Case 01 overlaps the worked example Claude Code gave in chat (steps 2, 4, 5, 7). Its baseline is not blind.
