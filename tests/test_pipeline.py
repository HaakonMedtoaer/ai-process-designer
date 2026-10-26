from pathlib import Path
from types import SimpleNamespace

import pytest

from allocator import llm, pipeline
from allocator.rules import Role

FIXTURE = Path(__file__).parent / "fixtures" / "sample_analysis.json"


@pytest.fixture
def analysis():
    return pipeline.load(FIXTURE)


def test_volume_left_unknown_blocks_every_step(analysis):
    results = pipeline.allocate_steps(analysis, volume={})
    assert all(r.allocation.needs_input for r in results)
    assert all("volume" in r.allocation.missing for r in results)


def test_allocation_with_volume(analysis):
    results = pipeline.allocate_steps(analysis, volume={1: 3, 2: 3, 3: 3})
    roles = [r.allocation.role for r in results]
    assert roles == [Role.SCRIPT, Role.AGENT, None]  # step 3 has an unknown score


def test_model_unknown_is_kept_unless_user_overrides(analysis):
    vol = {1: 3, 2: 3, 3: 3}
    # G0 runs before G1, so a model 'unknown' blocks even a clear accountability case
    r3 = pipeline.allocate_steps(analysis, vol)[2]
    assert r3.allocation.needs_input and r3.allocation.missing == ["verifiability"]
    fixed = pipeline.allocate_steps(analysis, vol, overrides={3: {"verifiability": 2}})[2]
    assert fixed.allocation.role is Role.HUMAN and fixed.allocation.fired == ["G1"]


def test_mermaid_has_one_node_per_step_and_fallback_edge(analysis):
    results = pipeline.allocate_steps(analysis, {1: 3, 2: 3, 3: 3})
    text = pipeline.mermaid(results)
    assert text.startswith("flowchart LR")
    for n in (1, 2, 3):
        assert f"S{n}[" in text
    assert "S2 -. " in text and "S1 -. " not in text
    assert "S1 --> S2" in text and "S2 --> S3" in text


def test_risks_name_gaps_agents_and_open_questions(analysis):
    results = pipeline.allocate_steps(analysis, {1: 3, 2: 3})
    text = "\n".join(pipeline.risks(results, analysis))
    assert "Step 3: not allocated" in text
    assert "Step 2: agent" in text
    assert "Open question: Fixture question." in text


def test_save_and_load_round_trip(analysis, tmp_path):
    path = tmp_path / "a.json"
    pipeline.save(analysis, path)
    assert pipeline.load(path) == analysis


# Model call, with a fake client (no network, no API key)

class FakeMessages:
    def __init__(self, response):
        self.response, self.kwargs = response, None

    def parse(self, **kwargs):
        self.kwargs = kwargs
        return self.response


def fake_client(response):
    messages = FakeMessages(response)
    return SimpleNamespace(beta=SimpleNamespace(messages=messages)), messages


def test_analyse_returns_parsed_output_and_sends_schema(analysis):
    client, messages = fake_client(SimpleNamespace(stop_reason="end_turn", parsed_output=analysis))
    assert llm.analyse("text", client=client) == analysis
    assert messages.kwargs["output_format"] is llm.Analysis
    assert messages.kwargs["messages"][0]["content"] == "text"


@pytest.mark.parametrize("stop", ["refusal", "max_tokens"])
def test_analyse_raises_on_bad_stop(stop):
    client, _ = fake_client(SimpleNamespace(stop_reason=stop, parsed_output=None))
    with pytest.raises(llm.AnalysisError):
        llm.analyse("text", client=client)


def test_analyse_raises_when_nothing_parsed():
    client, _ = fake_client(SimpleNamespace(stop_reason="end_turn", parsed_output=None))
    with pytest.raises(llm.AnalysisError):
        llm.analyse("text", client=client)
