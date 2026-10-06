"""Tests for secondary endpoints, engagement metrics, Holm adjustment, and sensitivity analyses."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from experimentguard.effects import (
    calculate_engagement_analysis,
    calculate_outlier_sensitivity,
    calculate_primary_bootstrap_sensitivity,
    run_secondary_and_sensitivity_analysis,
)


@pytest.fixture
def sample_experiment_df() -> pd.DataFrame:
    # 500 control, 500 treatment
    rng = np.random.default_rng(123)
    n = 500
    uids = list(range(1, 2 * n + 1))
    versions = ["gate_30"] * n + ["gate_40"] * n
    # gate_30: 45% r1, 20% r7, rounds ~ Gamma(2, 10)
    # gate_40: 44% r1, 18% r7, rounds ~ Gamma(2, 9.5)
    r1_ctrl = rng.random(n) < 0.45
    r7_ctrl = rng.random(n) < 0.20
    rounds_ctrl = np.round(rng.gamma(shape=2, scale=10, size=n)).astype(int)

    r1_treat = rng.random(n) < 0.44
    r7_treat = rng.random(n) < 0.18
    rounds_treat = np.round(rng.gamma(shape=2, scale=9.5, size=n)).astype(int)

    # Insert an extreme outlier in treatment to test outlier sensitivity
    rounds_treat[0] = 5000

    return pd.DataFrame(
        {
            "userid": uids,
            "version": versions,
            "sum_gamerounds": np.concatenate([rounds_ctrl, rounds_treat]),
            "retention_1": np.concatenate([r1_ctrl, r1_treat]),
            "retention_7": np.concatenate([r7_ctrl, r7_treat]),
        }
    )


def test_engagement_analysis(sample_experiment_df: pd.DataFrame):
    eng = calculate_engagement_analysis(sample_experiment_df)
    assert eng.metric == "sum_gamerounds"
    assert eng.control_summary.n == 500
    assert eng.treatment_summary.n == 500
    assert eng.control_summary.mean > 0
    assert eng.treatment_summary.mean > 0
    assert eng.control_summary.p99 <= eng.control_summary.max
    assert eng.treatment_summary.max >= 5000  # extreme outlier present
    assert eng.test_method == "welch_ttest"


def test_outlier_sensitivity(sample_experiment_df: pd.DataFrame):
    sens = calculate_outlier_sensitivity(sample_experiment_df, cap_percentile=99.0)
    assert sens.cap_percentile == 99.0
    assert sens.cap_value < 5000
    assert sens.treatment_capped_count >= 1
    # Outlier pulled the raw mean difference; capping dampens the extreme value
    assert sens.control_capped_mean <= sens.cap_value
    assert sens.treatment_capped_mean <= sens.cap_value


def test_bootstrap_sensitivity_reproducibility(sample_experiment_df: pd.DataFrame):
    boot1 = calculate_primary_bootstrap_sensitivity(sample_experiment_df, replicates=1000, seed=42)
    boot2 = calculate_primary_bootstrap_sensitivity(sample_experiment_df, replicates=1000, seed=42)
    assert boot1.bootstrap_ci_absolute[0] == pytest.approx(
        boot2.bootstrap_ci_absolute[0], abs=1e-12
    )
    assert boot1.bootstrap_ci_absolute[1] == pytest.approx(
        boot2.bootstrap_ci_absolute[1], abs=1e-12
    )


def test_secondary_and_sensitivity_suite(sample_experiment_df: pd.DataFrame):
    sec = run_secondary_and_sensitivity_analysis(
        sample_experiment_df,
        control_arm="gate_30",
        treatment_arm="gate_40",
        seed=42,
        bootstrap_replicates=1000,
    )
    assert sec.day1_retention.metric == "retention_1"
    assert "retention_1_holm" in sec.holm_family_pvalues
    assert "sum_gamerounds_holm" in sec.holm_family_pvalues
    assert sec.holm_family_pvalues["retention_1_holm"] >= sec.holm_family_pvalues["retention_1_raw"]
    assert sec.outlier_sensitivity.treatment_capped_count >= 1
