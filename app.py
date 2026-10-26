"""Streamlit page. Run with: streamlit run app.py"""

import math
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from allocator import pipeline
from allocator.business_case import Range, StepInputs, compute
from allocator.llm import AnalysisError, analyse

ROOT = Path(__file__).parent
CASES = sorted((ROOT / "cases").glob("*/process.md"))
SAVED = ROOT / "results"
SCORE_OPTIONS = ["1", "2", "3", "unknown"]
SHORT = {"variability": "V", "error_cost": "E", "verifiability": "C",
         "accountability": "A", "access_risk": "R", "volume": "Q"}

st.set_page_config(page_title="Process allocator", layout="wide")
st.title("Process allocator")
st.caption("Script, AI call, agent or human, step by step. The simplest option that works wins.")


def case_text(path: Path) -> str:
    text = path.read_text()
    start = text.find("## Process text")
    end = text.find("## Sources")
    body = text[start:end].split("\n", 1)[1]
    return body.replace("(paste this into the tool)", "").strip()


def blank(v):
    return v is None or (isinstance(v, float) and math.isnan(v))


# 1. Input
with st.sidebar:
    st.header("Input")
    mode = st.radio("Source", ["Analyse text (needs API key)", "Load saved analysis"])
    if mode.startswith("Load"):
        files = sorted(SAVED.glob("*.json")) if SAVED.exists() else []
        if not files:
            st.info("No saved analyses in results/ yet.")
        else:
            choice = st.selectbox("Saved analysis", files, format_func=lambda p: p.stem)
            if st.button("Load"):
                st.session_state.analysis = pipeline.load(choice)
                st.session_state.name = choice.stem

if mode.startswith("Analyse"):
    example = st.selectbox("Start from a test case (optional)", [None] + CASES,
                           format_func=lambda p: "-" if p is None else p.parent.name)
    text = st.text_area("Process description", height=260,
                        value=case_text(example) if example else "")
    if st.button("Analyse", type="primary", disabled=not text.strip()):
        with st.spinner("Asking the model for steps and scores..."):
            try:
                st.session_state.analysis = analyse(text)
                st.session_state.name = example.parent.name if example else "custom"
            except AnalysisError as e:
                st.error(str(e))
            except Exception as e:  # missing key, network, API errors
                st.error(f"Model call failed: {e}")

analysis = st.session_state.get("analysis")
if analysis is None:
    st.stop()

# 2. Scores (editable) and allocation
st.header("Steps and scores")
st.write("Model scores are proposals. Change any score; the allocation updates. "
         "Volume (Q) is yours to set: 1 rare, 2 moderate, 3 high.")
default_q = st.selectbox("Volume (Q) for all steps, adjust per step below", SCORE_OPTIONS,
                         index=3)
rows = []
for s in analysis.steps:
    row = {"#": s.number, "Step": s.name}
    for c in pipeline.MODEL_CRITERIA:
        row[SHORT[c]] = getattr(s, c).score
    row["Q"] = default_q
    rows.append(row)
config = {SHORT[c]: st.column_config.SelectboxColumn(options=SCORE_OPTIONS, required=True)
          for c in SHORT}
edited = st.data_editor(pd.DataFrame(rows), column_config=config, hide_index=True,
                        disabled=["#", "Step"], key=f"scores-{default_q}")

volume, overrides = {}, {}
for _, r in edited.iterrows():
    n = int(r["#"])
    volume[n] = None if r["Q"] == "unknown" else int(r["Q"])
    overrides[n] = {c: (None if r[SHORT[c]] == "unknown" else int(r[SHORT[c]]))
                    for c in pipeline.MODEL_CRITERIA}
results = pipeline.allocate_steps(analysis, volume, overrides)

st.header("Allocation")
st.dataframe(pd.DataFrame([{
    "#": r.step.number, "Step": r.step.name, "Role": pipeline.label(r.allocation),
    "Fallback": r.allocation.fallback.value if r.allocation.fallback else "",
    "Rules": " ".join(r.allocation.fired)} for r in results]), hide_index=True)

for r in results:
    with st.expander(f"{r.step.number}. {r.step.name}: {pipeline.label(r.allocation)}"):
        st.write(r.step.description)
        for line in pipeline.explain(r.allocation):
            st.markdown(f"- {line}")
        for c in pipeline.MODEL_CRITERIA:
            cs = getattr(r.step, c)
            quote = f' *"{cs.quote}"*' if cs.quote else ""
            st.markdown(f"**{c}** = {cs.score}. {cs.reason}{quote}")

# 3. Diagram
st.header("Redesigned workflow")
diagram = pipeline.mermaid(results)
components.html(f"""
<pre class="mermaid">{diagram}</pre>
<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs";
mermaid.initialize({{startOnLoad: true}});
</script>""", height=320, scrolling=True)
with st.expander("Mermaid source"):
    st.code(diagram, language="text")

# 4. Business case
st.header("Business case")
st.write("All numbers are yours. Leave a cell empty if you don't know; the step is then "
         "reported as missing instead of estimated. Tick 'measured' only for numbers you measured.")
hourly = st.number_input("Hourly cost", min_value=0.0, value=None, step=50.0)
bc_rows = [{"#": r.step.number, "Step": r.step.name, "Role": pipeline.label(r.allocation),
            "Volume / month": None, "Minutes / item": None,
            "Fallback % low": None, "Fallback % high": None, "Fallback measured": False,
            "Review min low": None, "Review min high": None, "Review measured": False}
           for r in results]
bc = st.data_editor(pd.DataFrame(bc_rows), hide_index=True, disabled=["#", "Step", "Role"],
                    key="bc")

inputs, problems = [], []
for r, (_, row) in zip(results, bc.iterrows()):
    def rng(lo, hi, scale=1.0):
        if blank(row[lo]) or blank(row[hi]):
            return None
        return Range(float(row[lo]) / scale, float(row[hi]) / scale)
    try:
        inputs.append(StepInputs(
            name=f"{r.step.number}. {r.step.name}", allocation=r.allocation,
            volume_per_month=None if blank(row["Volume / month"]) else float(row["Volume / month"]),
            minutes_per_item=None if blank(row["Minutes / item"]) else float(row["Minutes / item"]),
            fallback_share=rng("Fallback % low", "Fallback % high", 100),
            review_minutes=rng("Review min low", "Review min high"),
            fallback_share_verified=bool(row["Fallback measured"]),
            review_minutes_verified=bool(row["Review measured"])))
    except ValueError as e:
        problems.append(f"Step {r.step.number}: {e}")

for p in problems:
    st.error(p)
if not problems:
    try:
        case = compute(inputs, hourly)
    except ValueError as e:
        st.error(str(e))
        case = None
    if case:
        if case.total_saving:
            st.metric("Monthly saving range",
                      f"{case.total_saving.low:,.0f} to {case.total_saving.high:,.0f}")
        else:
            st.warning("No total yet. Some steps are missing inputs (listed below).")
        st.dataframe(pd.DataFrame([{
            "Step": s.name,
            "Current cost": "" if s.current_cost is None else f"{s.current_cost:,.0f}",
            "Saving low": "" if s.saving is None else f"{s.saving.low:,.0f}",
            "Saving high": "" if s.saving is None else f"{s.saving.high:,.0f}",
            "Missing": ", ".join(s.missing),
            "Unverified": ", ".join(s.unverified)} for s in case.steps]), hide_index=True)
        drivers = case.drivers()
        if drivers:
            st.write("**Biggest savings:** " + ", ".join(d.name for d in drivers[:3]))
        st.write("**Assumptions**")
        for a in case.assumptions:
            st.markdown(f"- {a}")

# 5. Risks
st.header("Risks and open questions")
for line in pipeline.risks(results, analysis):
    st.markdown(f"- {line}")

# Save
st.divider()
name = st.text_input("Save this analysis as", value=st.session_state.get("name", "custom"))
if st.button("Save to results/"):
    SAVED.mkdir(exist_ok=True)
    pipeline.save(analysis, SAVED / f"{name}.json")
    st.success(f"Saved results/{name}.json")
