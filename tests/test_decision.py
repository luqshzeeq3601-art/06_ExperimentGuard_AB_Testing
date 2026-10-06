"""Tests for pure deterministic decision rules and evidence qualifications."""

from __future__ import annotations

from experimentguard.decision import evaluate_decision
from experimentguard.effects import BinaryEffectResult
from experimentguard.integrity import IntegrityReport


def make_mock_integrity(
    status: str = "provisional",
    srm_status: str = "pass",
    assignment_evidence: str = "reported",
    blockers: list[str] | None = None,
) -> IntegrityReport:
    return IntegrityReport(
        status=status,
        assignment_evidence=assignment_evidence,
        allocation_evidence="assumed",
        maturity_evidence="unknown",
        n_control=1000,
        n_treatment=1000,
        n_total=2000,
        expected_treatment_fraction=0.5,
        observed_treatment_fraction=0.5,
        srm_pvalue=1.0,
        srm_threshold=0.001,
        srm_status=srm_status,
        blockers=blockers or [],
        limitations=[],
    )


def make_mock_effect(
    ci_low: float,
    ci_high: float,
    pvalue: float,
) -> BinaryEffectResult:
    return BinaryEffectResult(
        metric="retention_7",
        control="gate_30",
        treatment="gate_40",
        n_control=1000,
        n_treatment=1000,
        retained_control=200,
        retained_treatment=250,
        rate_control=0.20,
        rate_treatment=0.25,
        rate_control_ci=(0.17, 0.23),
        rate_treatment_ci=(0.22, 0.28),
        effect_absolute=0.05,
        effect_percentage_points=5.0,
        relative_change_percent=25.0,
        relative_change_unavailable_reason=None,
        ci_absolute=(ci_low, ci_high),
        confidence_level=0.95,
        confidence_method="newcomb",
        pvalue=pvalue,
        test_method="z_test",
        alternative="two-sided",
    )


def test_decision_blocked():
    # 1. SRM failure
    integ_srm = make_mock_integrity(status="fail", srm_status="fail", blockers=["SRM fail"])
    eff = make_mock_effect(0.01, 0.05, 0.001)
    dec = evaluate_decision(integ_srm, eff)
    assert dec.status == "blocked"

    # 2. Unverified assignment
    integ_unv = make_mock_integrity(assignment_evidence="unverified")
    dec_unv = evaluate_decision(integ_unv, eff)
    assert dec_unv.status == "blocked"

    # 3. None primary effect
    integ_ok = make_mock_integrity()
    dec_none = evaluate_decision(integ_ok, None)
    assert dec_none.status == "blocked"


def test_decision_supported():
    # L > 0.005 and p < 0.05
    integ = make_mock_integrity()
    eff = make_mock_effect(ci_low=0.006, ci_high=0.030, pvalue=0.002)
    dec = evaluate_decision(integ, eff, d_min=0.005, alpha=0.05)
    assert dec.status == "supported"
    assert dec.is_harm_detected is False
    assert dec.evidence_qualification == "provisional"


def test_decision_not_supported_harm():
    # U < 0.0 -> harm
    integ = make_mock_integrity()
    eff = make_mock_effect(ci_low=-0.030, ci_high=-0.002, pvalue=0.01)
    dec = evaluate_decision(integ, eff, d_min=0.005, alpha=0.05)
    assert dec.status == "not_supported"
    assert dec.is_harm_detected is True
    assert "evidence_of_harm" in dec.reason_codes


def test_decision_not_supported_small_effect():
    # U < 0.005 but U >= 0
    integ = make_mock_integrity()
    eff = make_mock_effect(ci_low=-0.001, ci_high=0.004, pvalue=0.20)
    dec = evaluate_decision(integ, eff, d_min=0.005, alpha=0.05)
    assert dec.status == "not_supported"
    assert dec.is_harm_detected is False


def test_decision_inconclusive_covers_threshold():
    # CI encompasses 0.005 (e.g. [-0.002, 0.015])
    integ = make_mock_integrity()
    eff = make_mock_effect(ci_low=-0.002, ci_high=0.015, pvalue=0.03)
    dec = evaluate_decision(integ, eff, d_min=0.005, alpha=0.05)
    assert dec.status == "inconclusive"


def test_decision_boundary_cases():
    integ = make_mock_integrity()

    # L == 0.005 exactly -> inconclusive
    eff_l_eq = make_mock_effect(ci_low=0.005, ci_high=0.020, pvalue=0.01)
    dec_l = evaluate_decision(integ, eff_l_eq, d_min=0.005, alpha=0.05)
    assert dec_l.status == "inconclusive"

    # p == 0.05 exactly -> cannot support
    eff_p_eq = make_mock_effect(ci_low=0.008, ci_high=0.025, pvalue=0.05)
    dec_p = evaluate_decision(integ, eff_p_eq, d_min=0.005, alpha=0.05)
    assert dec_p.status == "inconclusive"
