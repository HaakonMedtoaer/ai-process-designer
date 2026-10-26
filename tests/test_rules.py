import pytest

from allocator.rules import Role, Scores, allocate


def scores(**kw):
    base = dict(variability=2, error_cost=1, verifiability=1,
                accountability=1, access_risk=1, volume=3)
    base.update(kw)
    return Scores(**base)


# Gates

def test_unknown_score_blocks_allocation_and_names_the_gap():
    a = allocate(scores(verifiability=None, volume=None))
    assert a.needs_input
    assert a.missing == ["verifiability", "volume"]
    assert a.fired == ["G0"]


def test_named_owner_means_human_even_for_simple_input():
    a = allocate(scores(variability=1, accountability=3))
    assert a.role is Role.HUMAN and a.fired == ["G1"]


def test_low_volume_is_not_worth_automating():
    a = allocate(scores(variability=1, volume=1))
    assert a.role is Role.HUMAN and a.fired == ["G2"]


def test_risky_access_with_uncheckable_output_stays_human():
    a = allocate(scores(variability=3, access_risk=3, verifiability=3))
    assert a.role is Role.HUMAN and a.fired == ["G3"]


def test_out_of_range_score_is_rejected():
    with pytest.raises(ValueError):
        scores(variability=4)


# Ladder: prefer the lowest rung

def test_fixed_format_gets_a_script_not_an_agent():
    a = allocate(scores(variability=1, error_cost=3, access_risk=2))
    assert a.role is Role.SCRIPT
    assert not a.human_review and a.fallback is None


def test_messy_input_gets_a_single_ai_call():
    a = allocate(scores(variability=2))
    assert a.role is Role.AI_CALL


def test_unpredictable_path_with_checkable_output_gets_an_agent():
    a = allocate(scores(variability=3, verifiability=2))
    assert a.role is Role.AGENT


def test_unpredictable_path_with_uncheckable_output_stays_human():
    a = allocate(scores(variability=3, verifiability=3))
    assert a.role is Role.HUMAN and a.fired == ["L4"]


# Review overlay

def test_rule_checkable_ai_output_needs_no_review():
    a = allocate(scores(variability=2, error_cost=3, verifiability=1))
    assert not a.human_review


def test_costly_mistakes_with_person_checkable_output_get_review():
    a = allocate(scores(variability=2, error_cost=2, verifiability=2))
    assert a.human_review and "H1" in a.fired


def test_agent_with_sensitive_access_gets_review():
    a = allocate(scores(variability=3, verifiability=1, access_risk=2))
    assert a.role is Role.AGENT and a.human_review and "H2" in a.fired


def test_agent_with_irreversible_mistakes_always_gets_review():
    a = allocate(scores(variability=3, verifiability=1, error_cost=3))
    assert a.human_review and "H3" in a.fired


# Fallback

@pytest.mark.parametrize("v,c", [(2, 1), (3, 2)])
def test_ai_and_agent_steps_fall_back_to_a_human(v, c):
    a = allocate(scores(variability=v, verifiability=c))
    assert a.fallback is Role.HUMAN and a.fired[-1] == "F1"
