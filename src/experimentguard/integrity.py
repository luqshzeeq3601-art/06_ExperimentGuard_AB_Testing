"""Integrity diagnostics, sample ratio mismatch (SRM) tests, and evidence classification."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scipy.stats import binomtest

from experimentguard.config import ExperimentConfig
from experimentguard.data import ValidationReport


@dataclass
class IntegrityReport:
    status: str  # "pass" | "provisional" | "fail"
    assignment_evidence: str  # "verified" | "reported" | "unverified"
    allocation_evidence: str  # "verified" | "assumed"
    maturity_evidence: str  # "verified" | "unknown"
    n_control: int
    n_treatment: int
    n_total: int
    expected_treatment_fraction: float
    observed_treatment_fraction: float
    srm_pvalue: float
    srm_threshold: float
    srm_status: str  # "pass" | "fail"
    blockers: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "assignment_evidence": self.assignment_evidence,
            "allocation_evidence": self.allocation_evidence,
            "maturity_evidence": self.maturity_evidence,
            "n_control": self.n_control,
            "n_treatment": self.n_treatment,
            "n_total": self.n_total,
            "expected_treatment_fraction": self.expected_treatment_fraction,
            "observed_treatment_fraction": self.observed_treatment_fraction,
            "srm_pvalue": self.srm_pvalue,
            "srm_threshold": self.srm_threshold,
            "srm_status": self.srm_status,
            "blockers": self.blockers,
            "limitations": self.limitations,
        }


def check_integrity(
    validation_report: ValidationReport,
    config: ExperimentConfig,
    manifest_path: str | Path | None = None,
) -> IntegrityReport:
    """Run SRM binomial test and assess evidence quality from manifest and config."""
    nA = validation_report.arm_counts.get(config.control, 0)
    nB = validation_report.arm_counts.get(config.treatment, 0)
    n_total = nA + nB

    qB = config.expected_treatment_fraction
    srm_thresh = config.srm_alpha

    # Read manifest if available
    manifest_data: dict[str, Any] = {}
    if manifest_path is not None:
        p = Path(manifest_path)
        if p.is_file():
            try:
                manifest_data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass

    assignment_ev = manifest_data.get("assignment_evidence", "reported")
    allocation_ev = manifest_data.get("expected_allocation_evidence", config.allocation_evidence)
    maturity_ev = manifest_data.get("maturity_evidence", "unknown")

    blockers: list[str] = list(validation_report.blockers)
    limitations: list[str] = []

    if not validation_report.is_valid or n_total == 0:
        return IntegrityReport(
            status="fail",
            assignment_evidence=assignment_ev,
            allocation_evidence=allocation_ev,
            maturity_evidence=maturity_ev,
            n_control=nA,
            n_treatment=nB,
            n_total=n_total,
            expected_treatment_fraction=qB,
            observed_treatment_fraction=0.0,
            srm_pvalue=0.0,
            srm_threshold=srm_thresh,
            srm_status="fail",
            blockers=blockers,
            limitations=["Dataset validation failed; integrity checks aborted."],
        )

    # Binomial SRM test
    binom_res = binomtest(k=nB, n=n_total, p=qB, alternative="two-sided")
    srm_pval = float(binom_res.pvalue)
    obs_fraction = nB / n_total

    srm_pass = srm_pval >= srm_thresh
    srm_status = "pass" if srm_pass else "fail"

    if not srm_pass:
        blockers.append(
            f"Sample Ratio Mismatch detected: p={srm_pval:.6g} < threshold {srm_thresh} "
            f"(observed fraction {obs_fraction:.4f} vs expected {qB:.4f})"
        )

    if assignment_ev == "unverified":
        blockers.append("Assignment evidence is unverified; causal interpretation blocked.")
    elif assignment_ev == "reported":
        limitations.append(
            "Random assignment is source-reported but not independently verifiable via server logs."
        )

    if allocation_ev == "assumed":
        limitations.append(
            "Expected 50:50 allocation is assumed; SRM tested under assumed allocation."
        )

    if maturity_ev == "unknown":
        limitations.append(
            "Maturity evidence unknown: installation timestamps and cohort cutoffs are absent."
        )

    for lim in manifest_data.get("unresolved_limitations", []):
        if lim not in limitations:
            limitations.append(lim)

    # Overall quality status
    if blockers or not srm_pass:
        status = "fail"
    elif assignment_ev == "verified" and allocation_ev == "verified" and maturity_ev == "verified":
        status = "pass"
    else:
        status = "provisional"

    return IntegrityReport(
        status=status,
        assignment_evidence=assignment_ev,
        allocation_evidence=allocation_ev,
        maturity_evidence=maturity_ev,
        n_control=nA,
        n_treatment=nB,
        n_total=n_total,
        expected_treatment_fraction=qB,
        observed_treatment_fraction=obs_fraction,
        srm_pvalue=srm_pval,
        srm_threshold=srm_thresh,
        srm_status=srm_status,
        blockers=blockers,
        limitations=limitations,
    )
