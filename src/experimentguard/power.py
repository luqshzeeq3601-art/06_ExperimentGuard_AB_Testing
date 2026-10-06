"""Prospective sample size and statistical power planning for two-variant proportions."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import pandas as pd
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize


@dataclass
class PowerScenarioResult:
    scenario_id: str
    baseline_rate: float
    mde_absolute: float
    mde_percentage_points: float
    treatment_rate: float
    alpha: float
    target_power: float
    expected_treatment_fraction: float
    allocation_ratio: float
    cohens_h: float
    required_n_control: int
    required_n_treatment: int
    required_n_total: int
    achieved_power: float
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "baseline_rate": self.baseline_rate,
            "mde_absolute": self.mde_absolute,
            "mde_percentage_points": self.mde_percentage_points,
            "treatment_rate": self.treatment_rate,
            "alpha": self.alpha,
            "target_power": self.target_power,
            "expected_treatment_fraction": self.expected_treatment_fraction,
            "allocation_ratio": self.allocation_ratio,
            "cohens_h": self.cohens_h,
            "required_n_control": self.required_n_control,
            "required_n_treatment": self.required_n_treatment,
            "required_n_total": self.required_n_total,
            "achieved_power": self.achieved_power,
            "notes": self.notes,
        }


def plan_sample_size_scenario(
    *,
    baseline_rate: float = 0.20,
    mde_absolute: float = 0.005,
    alpha: float = 0.05,
    target_power: float = 0.80,
    expected_treatment_fraction: float = 0.50,
    scenario_id: str = "default",
) -> PowerScenarioResult:
    """Calculate prospective required sample size per arm and total for given MDE and baseline.

    Uses Cohen's h and NormalIndPower two-sided solver.
    """
    if not (0.0 < baseline_rate < 1.0):
        raise ValueError(f"baseline_rate must be in (0, 1), got {baseline_rate}")
    if mde_absolute <= 0:
        raise ValueError(f"mde_absolute must be positive, got {mde_absolute}")
    if baseline_rate + mde_absolute >= 1.0:
        raise ValueError(f"baseline_rate + mde must be < 1.0, got {baseline_rate} + {mde_absolute}")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    if not (0.0 < target_power < 1.0):
        raise ValueError(f"target_power must be in (0, 1), got {target_power}")
    if not (0.0 < expected_treatment_fraction < 1.0):
        raise ValueError(
            f"expected_treatment_fraction must be in (0, 1), got {expected_treatment_fraction}"
        )

    p0 = baseline_rate
    p1 = p0 + mde_absolute
    qB = expected_treatment_fraction
    ratio = qB / (1.0 - qB)  # nB / nA

    # Cohen's h effect size for two proportions
    h = abs(float(proportion_effectsize(p1, p0)))

    solver = NormalIndPower()
    raw_nA = solver.solve_power(
        effect_size=h,
        nobs1=None,
        alpha=alpha,
        power=target_power,
        ratio=ratio,
        alternative="two-sided",
    )

    # Round up integer sample sizes
    nA = math.ceil(raw_nA)
    nB = math.ceil(ratio * nA)
    n_total = nA + nB

    # Verify achieved power with rounded integer arm sizes
    actual_ratio = nB / nA
    achieved_power = float(
        solver.solve_power(
            effect_size=h,
            nobs1=nA,
            alpha=alpha,
            power=None,
            ratio=actual_ratio,
            alternative="two-sided",
        )
    )

    return PowerScenarioResult(
        scenario_id=scenario_id,
        baseline_rate=p0,
        mde_absolute=mde_absolute,
        mde_percentage_points=100.0 * mde_absolute,
        treatment_rate=p1,
        alpha=alpha,
        target_power=target_power,
        expected_treatment_fraction=qB,
        allocation_ratio=ratio,
        cohens_h=h,
        required_n_control=nA,
        required_n_treatment=nB,
        required_n_total=n_total,
        achieved_power=achieved_power,
        notes="Plans detection against H0: delta=0 with two-sided test.",
    )


def plan_power_scenarios(
    baseline_rate: float = 0.20,
    mde_list: list[float] | None = None,
    alpha: float = 0.05,
    target_power: float = 0.80,
    expected_treatment_fraction: float = 0.50,
) -> list[PowerScenarioResult]:
    """Generate power planning table for multiple MDE scenarios."""
    if mde_list is None:
        mde_list = [0.0025, 0.005, 0.01]

    results: list[PowerScenarioResult] = []
    for mde in mde_list:
        sc_id = f"mde_{mde * 100:.2f}pp"
        res = plan_sample_size_scenario(
            baseline_rate=baseline_rate,
            mde_absolute=mde,
            alpha=alpha,
            target_power=target_power,
            expected_treatment_fraction=expected_treatment_fraction,
            scenario_id=sc_id,
        )
        results.append(res)
    return results


def power_scenarios_to_dataframe(scenarios: list[PowerScenarioResult]) -> pd.DataFrame:
    """Convert list of PowerScenarioResult into a structured DataFrame."""
    records = [s.to_dict() for s in scenarios]
    return pd.DataFrame.from_records(records)
