"""Tests for prospective power planning and sample size calculations."""

from __future__ import annotations

import pytest

from experimentguard.power import (
    plan_power_scenarios,
    plan_sample_size_scenario,
    power_scenarios_to_dataframe,
)


def test_power_scenario_monotonicity():
    # Smaller MDE must require strictly larger sample size
    sc_small = plan_sample_size_scenario(baseline_rate=0.20, mde_absolute=0.0025)
    sc_mid = plan_sample_size_scenario(baseline_rate=0.20, mde_absolute=0.005)
    sc_large = plan_sample_size_scenario(baseline_rate=0.20, mde_absolute=0.01)

    assert sc_small.required_n_total > sc_mid.required_n_total > sc_large.required_n_total
    assert sc_small.achieved_power >= 0.80
    assert sc_mid.achieved_power >= 0.80
    assert sc_large.achieved_power >= 0.80


def test_power_scenario_equal_allocation():
    sc = plan_sample_size_scenario(
        baseline_rate=0.20,
        mde_absolute=0.005,
        alpha=0.05,
        target_power=0.80,
        expected_treatment_fraction=0.50,
    )
    assert sc.required_n_control == sc.required_n_treatment
    assert sc.required_n_total == sc.required_n_control + sc.required_n_treatment
    assert sc.achieved_power >= 0.80


def test_power_scenario_unequal_allocation():
    # 60:40 allocation (qB = 0.60, ratio = 1.5)
    sc = plan_sample_size_scenario(
        baseline_rate=0.20,
        mde_absolute=0.005,
        expected_treatment_fraction=0.60,
    )
    assert sc.allocation_ratio == pytest.approx(1.5, abs=1e-8)
    assert sc.required_n_treatment >= int(1.5 * sc.required_n_control)
    assert sc.achieved_power >= 0.80


def test_power_scenarios_table():
    scenarios = plan_power_scenarios(
        baseline_rate=0.20,
        mde_list=[0.0025, 0.005, 0.01],
    )
    assert len(scenarios) == 3
    df = power_scenarios_to_dataframe(scenarios)
    assert len(df) == 3
    assert "required_n_total" in df.columns
    assert "achieved_power" in df.columns


def test_power_invalid_inputs():
    with pytest.raises(ValueError, match="baseline_rate must be in"):
        plan_sample_size_scenario(baseline_rate=1.5)
    with pytest.raises(ValueError, match="mde_absolute must be positive"):
        plan_sample_size_scenario(mde_absolute=-0.01)
    with pytest.raises(ValueError, match="baseline_rate \\+ mde must be < 1.0"):
        plan_sample_size_scenario(baseline_rate=0.95, mde_absolute=0.10)
    with pytest.raises(ValueError, match="target_power must be in"):
        plan_sample_size_scenario(target_power=1.0)
    with pytest.raises(ValueError, match="expected_treatment_fraction must be in"):
        plan_sample_size_scenario(expected_treatment_fraction=0.0)
