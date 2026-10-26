"""Numbers here are arithmetic fixtures for the formulas, not claims about any process."""

import pytest

from allocator.business_case import Range, StepInputs, compute
from allocator.rules import Allocation, Role

HOURLY = 60.0  # 1 per minute keeps the arithmetic readable


def step(role, review=False, fallback=None, **kw):
    alloc = Allocation(role=role, human_review=review, fallback=fallback)
    base = dict(name="s", allocation=alloc, volume_per_month=100, minutes_per_item=10)
    base.update(kw)
    return StepInputs(**base)


def test_script_saves_all_current_time():
    r = compute([step(Role.SCRIPT)], HOURLY)
    assert r.steps[0].current_cost == 1000
    assert r.total_saving == Range(1000, 1000)


def test_human_step_saves_nothing():
    r = compute([step(Role.HUMAN)], HOURLY)
    assert r.total_saving == Range(0, 0)


def test_ai_call_range_comes_from_fallback_share():
    r = compute([step(Role.AI_CALL, fallback=Role.HUMAN,
                      fallback_share=Range(0.1, 0.3))], HOURLY)
    # remaining manual time: 100 items x share x 10 min
    assert r.total_saving.low == pytest.approx(1000 - 300)
    assert r.total_saving.high == pytest.approx(1000 - 100)


def test_review_time_reduces_the_saving():
    r = compute([step(Role.AGENT, review=True, fallback=Role.HUMAN,
                      fallback_share=Range(0.0, 0.0), review_minutes=Range(1, 2))], HOURLY)
    assert r.total_saving == Range(1000 - 200, 1000 - 100)


def test_missing_inputs_are_reported_not_defaulted():
    r = compute([step(Role.AGENT, review=True, minutes_per_item=None)], HOURLY)
    s = r.steps[0]
    assert s.saving is None
    assert set(s.missing) == {"minutes_per_item", "fallback_share", "review_minutes"}
    assert r.total_saving is None


def test_missing_hourly_cost_blocks_everything():
    r = compute([step(Role.SCRIPT)], None)
    assert r.total_saving is None and r.steps[0].missing == ["hourly_cost"]


def test_unallocated_step_cannot_be_costed():
    r = compute([step(None)], HOURLY)
    assert "allocation" in r.steps[0].missing


def test_assumed_fallback_share_is_flagged_as_unverified():
    r = compute([step(Role.AI_CALL, fallback_share=Range(0.1, 0.1))], HOURLY)
    assert r.steps[0].unverified == ["fallback_share"]


def test_measured_inputs_are_not_flagged():
    r = compute([step(Role.AI_CALL, fallback_share=Range(0.1, 0.1),
                      fallback_share_verified=True)], HOURLY)
    assert r.steps[0].unverified == []


def test_drivers_are_sorted_by_saving():
    steps = [step(Role.HUMAN, name="h"),
             step(Role.SCRIPT, name="small", volume_per_month=10),
             step(Role.SCRIPT, name="big")]
    names = [s.name for s in compute(steps, HOURLY).drivers()]
    assert names == ["big", "small"]


def test_build_and_running_costs_are_stated_as_excluded():
    r = compute([step(Role.SCRIPT)], HOURLY)
    assert any("Excludes build and running costs" in a for a in r.assumptions)


def test_invalid_ranges_are_rejected():
    with pytest.raises(ValueError):
        Range(2, 1)
    with pytest.raises(ValueError):
        compute([step(Role.AI_CALL, fallback_share=Range(0.5, 1.5))], HOURLY)
