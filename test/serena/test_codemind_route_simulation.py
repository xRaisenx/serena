"""Offline schedule model only; not a Codex host scheduler acceptance test."""

import pytest

from tools.codemind_route_simulation import simulate_validations


def test_five_validation_jobs_never_exceed_three_active_slots():
    result = simulate_validations([("syntax", 2, True), ("unit", 4, True), ("regression", 3, True), ("audit", 1, True), ("docs", 1, True)])
    assert result["peak_active"] == 3
    assert result["completed"] == 5
    assert result["queued_at_start"] == 2
    assert result["events"][3]["start"] == 2
    assert result["makespan"] == 4


def test_unreclaimed_slot_is_quarantined_not_recycled():
    result = simulate_validations([("first", 1, False), ("second", 1, True)], max_slots=1)
    assert result["completed"] == 0
    assert result["quarantined"] == 1
    assert result["remaining"] == 1
    assert result["simulated_schedule_complete"] is False


def test_same_inputs_yield_same_bounded_schedule():
    values = [("source", 1, True), ("test", 2, True), ("review", 2, True)]
    assert simulate_validations(values) == simulate_validations(values)


def test_max_slots_is_strict_and_never_promotes_simulation_to_real_host_readiness():
    with pytest.raises(ValueError):
        simulate_validations([("job", 1, True)], max_slots=4)
    report = simulate_validations([("job", 1, True)])
    assert report["simulation_only"] is True
    assert "ready" not in report
