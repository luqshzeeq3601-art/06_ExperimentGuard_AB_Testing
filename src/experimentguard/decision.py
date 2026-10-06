"""Deterministic decision rules and interpretation for ExperimentGuard."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from experimentguard.effects import BinaryEffectResult
from experimentguard.integrity import IntegrityReport


@dataclass
class DecisionResult:
    status: str  # "supported" | "not_supported" | "inconclusive" | "blocked"
    reason_codes: list[str] = field(default_factory=list)
    explanation: str = ""
    practical_threshold_absolute: float = 0.005
    evidence_qualification: str = "provisional"  # "verified" | "provisional" | "unverified"
    is_harm_detected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason_codes": self.reason_codes,
            "explanation": self.explanation,
            "practical_threshold_absolute": self.practical_threshold_absolute,
            "evidence_qualification": self.evidence_qualification,
            "is_harm_detected": self.is_harm_detected,
        }


def evaluate_decision(
    integrity: IntegrityReport,
    primary_effect: BinaryEffectResult | None,
    d_min: float = 0.005,
    alpha: float = 0.05,
) -> DecisionResult:
    """Evaluate deterministic protocol decision rules in strict priority order.

    Rule Order:
    1. blocked: required quality fails, SRM fails, assignment unverified, or primary unavailable.
    2. supported: L > d_min and p < alpha (strict inequalities).
    3. not_supported: U < d_min (if U < 0, flags evidence_of_harm).
    4. inconclusive: all other valid cases (interval covers d_min, L <= d_min <= U, or p >= alpha).
    """
    evidence_qual = (
        "verified"
        if (
            integrity.assignment_evidence == "verified"
            and integrity.allocation_evidence == "verified"
            and integrity.maturity_evidence == "verified"
        )
        else "provisional"
    )

    # 1. Blocked
    if (
        integrity.status == "fail"
        or integrity.srm_status == "fail"
        or integrity.assignment_evidence == "unverified"
        or primary_effect is None
    ):
        reasons = list(integrity.blockers)
        if primary_effect is None and "Primary effect unavailable" not in reasons:
            reasons.append("Primary effect calculation is unavailable")
        return DecisionResult(
            status="blocked",
            reason_codes=["integrity_or_quality_blocked"] + reasons,
            explanation="Decision is blocked due to integrity failures, data invalidity, or unverified assignment.",
            practical_threshold_absolute=d_min,
            evidence_qualification="unverified"
            if integrity.assignment_evidence == "unverified"
            else "provisional",
            is_harm_detected=False,
        )

    L, U = primary_effect.ci_absolute
    pval = primary_effect.pvalue

    # 2. Supported: L > d_min and p < alpha
    if L > d_min and pval < alpha:
        return DecisionResult(
            status="supported",
            reason_codes=["lower_bound_exceeds_threshold", "statistically_significant"],
            explanation=(
                f"Evidence supports rollout: 95% CI lower bound ({L:.4f}) exceeds practical threshold "
                f"({d_min:.4f}) with p={pval:.4g} < {alpha}."
            ),
            practical_threshold_absolute=d_min,
            evidence_qualification=evidence_qual,
            is_harm_detected=False,
        )

    # 3. Not supported: U < d_min
    if U < d_min:
        is_harm = U < 0.0
        reasons = ["upper_bound_below_threshold"]
        if is_harm:
            reasons.append("evidence_of_harm")
            explanation = (
                f"Evidence does not support rollout: 95% CI upper bound ({U:.4f}) is strictly below 0.0, "
                f"indicating evidence consistent with a negative impact / retention decrease (harm)."
            )
        else:
            explanation = (
                f"Evidence does not support rollout: 95% CI upper bound ({U:.4f}) is strictly below practical "
                f"threshold ({d_min:.4f}). Any potential positive effect is too small to be practically meaningful."
            )
        return DecisionResult(
            status="not_supported",
            reason_codes=reasons,
            explanation=explanation,
            practical_threshold_absolute=d_min,
            evidence_qualification=evidence_qual,
            is_harm_detected=is_harm,
        )

    # 4. Inconclusive: L <= d_min <= U or p >= alpha
    return DecisionResult(
        status="inconclusive",
        reason_codes=["interval_covers_threshold_or_insufficient_precision"],
        explanation=(
            f"Result is inconclusive: 95% CI [{L:.4f}, {U:.4f}] encompasses practical threshold "
            f"({d_min:.4f}) or p={pval:.4g} >= {alpha}. Data lacks precision to confirm or rule out meaningful benefit."
        ),
        practical_threshold_absolute=d_min,
        evidence_qualification=evidence_qual,
        is_harm_detected=False,
    )
