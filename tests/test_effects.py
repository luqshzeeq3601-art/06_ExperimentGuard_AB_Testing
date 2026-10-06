"""Tests for binary effect estimation, Wilson CIs, Newcombe difference CIs, and hypothesis tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from experimentguard.effects import calculate_binary_effect


def test_standard_synthetic_arithmetic():
    res = calculate_binary_effect(xA=200, nA=1000, xB=250, nB=1000)
    assert res.rate_control == pytest.approx(0.20, abs=1e-12)
    assert res.rate_treatment == pytest.approx(0.25, abs=1e-12)
    assert res.effect_absolute == pytest.approx(0.05, abs=1e-12)
    assert res.effect_percentage_points == pytest.approx(5.0, abs=1e-12)
    assert res.relative_change_percent == pytest.approx(25.0, abs=1e-12)
    assert res.relative_change_unavailable_reason is None
    assert res.test_method == "z_test"
    assert res.ci_absolute[0] < res.effect_absolute < res.ci_absolute[1]


def test_direction_symmetry():
    # A=control, B=treatment
    res_fwd = calculate_binary_effect(xA=200, nA=1000, xB=250, nB=1000)
    # Swapped: A'=250/1000, B'=200/1000
    res_rev = calculate_binary_effect(xA=250, nA=1000, xB=200, nB=1000)

    assert res_fwd.effect_absolute == pytest.approx(-res_rev.effect_absolute, abs=1e-12)
    assert res_fwd.effect_percentage_points == pytest.approx(
        -res_rev.effect_percentage_points, abs=1e-12
    )
    assert res_fwd.ci_absolute[0] == pytest.approx(-res_rev.ci_absolute[1], abs=1e-8)
    assert res_fwd.ci_absolute[1] == pytest.approx(-res_rev.ci_absolute[0], abs=1e-8)
    assert res_fwd.pvalue == pytest.approx(res_rev.pvalue, abs=1e-8)


def test_equal_rates():
    res = calculate_binary_effect(xA=300, nA=1000, xB=300, nB=1000)
    assert res.effect_absolute == pytest.approx(0.0, abs=1e-12)
    assert res.effect_percentage_points == pytest.approx(0.0, abs=1e-12)
    assert res.relative_change_percent == pytest.approx(0.0, abs=1e-12)
    assert res.ci_absolute[0] < 0.0 < res.ci_absolute[1]
    assert res.pvalue == pytest.approx(1.0, abs=1e-8)


def test_zero_control_rate():
    res = calculate_binary_effect(xA=0, nA=500, xB=25, nB=500)
    assert res.rate_control == 0.0
    assert res.rate_treatment == pytest.approx(0.05, abs=1e-12)
    assert res.effect_absolute == pytest.approx(0.05, abs=1e-12)
    assert res.relative_change_percent is None
    assert "Control retention rate is 0.0" in (res.relative_change_unavailable_reason or "")
    assert res.ci_absolute[0] > 0.0


def test_constant_outcomes():
    # Both all-zero
    res_zero = calculate_binary_effect(xA=0, nA=100, xB=0, nB=100)
    assert res_zero.effect_absolute == 0.0
    assert res_zero.pvalue == 1.0
    assert res_zero.test_method == "exact_constant"
    # Finite interval, no false precision, symmetric around 0
    assert res_zero.ci_absolute[0] < 0.0 < res_zero.ci_absolute[1]
    assert res_zero.ci_absolute[0] == pytest.approx(-res_zero.ci_absolute[1], abs=1e-8)

    # Both all-one
    res_ones = calculate_binary_effect(xA=100, nA=100, xB=100, nB=100)
    assert res_ones.effect_absolute == 0.0
    assert res_ones.pvalue == 1.0
    assert res_ones.test_method == "exact_constant"
    assert res_ones.ci_absolute[0] < 0.0 < res_ones.ci_absolute[1]
    assert res_ones.ci_absolute[0] == pytest.approx(-res_ones.ci_absolute[1], abs=1e-8)


def test_small_cell_fisher_fallback():
    res = calculate_binary_effect(xA=1, nA=20, xB=4, nB=20)
    assert res.test_method == "fisher_exact"
    assert 0.0 <= res.pvalue <= 1.0


def test_load_fixtures_from_json():
    fixture_path = Path("tests/fixtures/binary_counts.json")
    assert fixture_path.is_file()
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    for case in data["test_cases"]:
        xA = case["xA"]
        nA = case["nA"]
        xB = case["xB"]
        nB = case["nB"]

        res = calculate_binary_effect(xA=xA, nA=nA, xB=xB, nB=nB)

        if "expected_rate_A" in case:
            assert res.rate_control == pytest.approx(case["expected_rate_A"], abs=1e-12)
        if "expected_rate_B" in case:
            assert res.rate_treatment == pytest.approx(case["expected_rate_B"], abs=1e-12)
        if "expected_delta" in case:
            assert res.effect_absolute == pytest.approx(case["expected_delta"], abs=1e-12)
        if "expected_delta_pp" in case:
            assert res.effect_percentage_points == pytest.approx(
                case["expected_delta_pp"], abs=1e-12
            )
        if "expected_relative_change_percent" in case:
            if case["expected_relative_change_percent"] is None:
                assert res.relative_change_percent is None
            else:
                assert res.relative_change_percent == pytest.approx(
                    case["expected_relative_change_percent"], abs=1e-12
                )
        if "expected_pvalue" in case:
            assert res.pvalue == pytest.approx(case["expected_pvalue"], abs=1e-8)
        if "expected_test_method" in case:
            assert res.test_method == case["expected_test_method"]
