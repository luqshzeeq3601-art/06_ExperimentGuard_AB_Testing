"""Binary proportion estimates, confidence intervals, hypothesis tests, and secondary/sensitivity analyses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, ttest_ind
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import (
    confint_proportions_2indep,
    proportion_confint,
    proportions_ztest,
)


@dataclass
class BinaryEffectResult:
    metric: str
    control: str
    treatment: str
    n_control: int
    n_treatment: int
    retained_control: int
    retained_treatment: int
    rate_control: float
    rate_treatment: float
    rate_control_ci: tuple[float, float]
    rate_treatment_ci: tuple[float, float]
    effect_absolute: float
    effect_percentage_points: float
    relative_change_percent: float | None
    relative_change_unavailable_reason: str | None
    ci_absolute: tuple[float, float]
    confidence_level: float
    confidence_method: str
    pvalue: float
    test_method: str
    alternative: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "control": self.control,
            "treatment": self.treatment,
            "n_control": self.n_control,
            "n_treatment": self.n_treatment,
            "retained_control": self.retained_control,
            "retained_treatment": self.retained_treatment,
            "rate_control": self.rate_control,
            "rate_treatment": self.rate_treatment,
            "rate_control_ci": list(self.rate_control_ci),
            "rate_treatment_ci": list(self.rate_treatment_ci),
            "effect_absolute": self.effect_absolute,
            "effect_percentage_points": self.effect_percentage_points,
            "relative_change_percent": self.relative_change_percent,
            "relative_change_unavailable_reason": self.relative_change_unavailable_reason,
            "ci_absolute": list(self.ci_absolute),
            "confidence_level": self.confidence_level,
            "confidence_method": self.confidence_method,
            "pvalue": self.pvalue,
            "test_method": self.test_method,
            "alternative": self.alternative,
        }


@dataclass
class ArmEngagementSummary:
    arm: str
    n: int
    mean: float
    std: float
    median: float
    zero_fraction: float
    p95: float
    p99: float
    max: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "n": self.n,
            "mean": self.mean,
            "std": self.std,
            "median": self.median,
            "zero_fraction": self.zero_fraction,
            "p95": self.p95,
            "p99": self.p99,
            "max": self.max,
        }


@dataclass
class EngagementAnalysisResult:
    metric: str
    control_summary: ArmEngagementSummary
    treatment_summary: ArmEngagementSummary
    mean_diff_absolute: float
    mean_diff_percent: float | None
    welch_t_stat: float
    welch_pvalue: float
    test_method: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "control_summary": self.control_summary.to_dict(),
            "treatment_summary": self.treatment_summary.to_dict(),
            "mean_diff_absolute": self.mean_diff_absolute,
            "mean_diff_percent": self.mean_diff_percent,
            "welch_t_stat": self.welch_t_stat,
            "welch_pvalue": self.welch_pvalue,
            "test_method": self.test_method,
        }


@dataclass
class OutlierSensitivityResult:
    cap_percentile: float
    cap_value: float
    control_capped_count: int
    treatment_capped_count: int
    control_capped_mean: float
    treatment_capped_mean: float
    original_mean_diff: float
    capped_mean_diff: float
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "cap_percentile": self.cap_percentile,
            "cap_value": self.cap_value,
            "control_capped_count": self.control_capped_count,
            "treatment_capped_count": self.treatment_capped_count,
            "control_capped_mean": self.control_capped_mean,
            "treatment_capped_mean": self.treatment_capped_mean,
            "original_mean_diff": self.original_mean_diff,
            "capped_mean_diff": self.capped_mean_diff,
            "notes": self.notes,
        }


@dataclass
class BootstrapSensitivityResult:
    replicates: int
    seed: int
    original_effect: float
    bootstrap_ci_absolute: tuple[float, float]
    bootstrap_ci_percentage_points: tuple[float, float]
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "replicates": self.replicates,
            "seed": self.seed,
            "original_effect": self.original_effect,
            "bootstrap_ci_absolute": list(self.bootstrap_ci_absolute),
            "bootstrap_ci_percentage_points": list(self.bootstrap_ci_percentage_points),
            "notes": self.notes,
        }


@dataclass
class SecondaryAnalysisResult:
    day1_retention: BinaryEffectResult
    engagement: EngagementAnalysisResult
    holm_family_pvalues: dict[str, float]
    outlier_sensitivity: OutlierSensitivityResult
    primary_bootstrap: BootstrapSensitivityResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "day1_retention": self.day1_retention.to_dict(),
            "engagement": self.engagement.to_dict(),
            "holm_family_pvalues": self.holm_family_pvalues,
            "outlier_sensitivity": self.outlier_sensitivity.to_dict(),
            "primary_bootstrap": self.primary_bootstrap.to_dict(),
        }


def calculate_binary_effect(
    *,
    xA: int,
    nA: int,
    xB: int,
    nB: int,
    metric_name: str = "retention_7",
    control_name: str = "gate_30",
    treatment_name: str = "gate_40",
    alpha: float = 0.05,
    method: str = "newcomb",
) -> BinaryEffectResult:
    """Calculate binary rates, Wilson CIs, Newcombe difference CI, and two-proportion test.

    B is treatment, A is control. Effect is B minus A.
    """
    if nA <= 0 or nB <= 0:
        raise ValueError(f"Denominators must be positive, got nA={nA}, nB={nB}")
    if not (0 <= xA <= nA):
        raise ValueError(f"Expected 0 <= xA <= nA, got xA={xA}, nA={nA}")
    if not (0 <= xB <= nB):
        raise ValueError(f"Expected 0 <= xB <= nB, got xB={xB}, nB={nB}")

    pA = xA / nA
    pB = xB / nB
    delta = pB - pA
    delta_pp = 100.0 * delta

    if pA > 0.0:
        rel_change: float | None = 100.0 * delta / pA
        rel_reason: str | None = None
    else:
        rel_change = None
        rel_reason = "Control retention rate is 0.0; relative change undefined."

    # Wilson intervals for individual arms
    ci_A_low, ci_A_high = proportion_confint(count=xA, nobs=nA, alpha=alpha, method="wilson")
    ci_B_low, ci_B_high = proportion_confint(count=xB, nobs=nB, alpha=alpha, method="wilson")
    rate_control_ci = (float(ci_A_low), float(ci_A_high))
    rate_treatment_ci = (float(ci_B_low), float(ci_B_high))

    # Newcombe interval for difference pB - pA
    ci_diff_low, ci_diff_high = confint_proportions_2indep(
        count1=xB,
        nobs1=nB,
        count2=xA,
        nobs2=nA,
        method=method,
        compare="diff",
        alpha=alpha,
    )
    ci_absolute = (float(ci_diff_low), float(ci_diff_high))

    # Check for constant identical outcomes
    is_constant_zero = xA == 0 and xB == 0
    is_constant_ones = xA == nA and xB == nB

    if is_constant_zero or is_constant_ones:
        pval = 1.0
        test_method = "exact_constant"
    else:
        # Check cell sizes for small-cell Fisher exact fallback (< 5)
        cell_table = [[xB, nB - xB], [xA, nA - xA]]
        min_cell = min(xB, nB - xB, xA, nA - xA)

        if min_cell < 5:
            _, pval_f = fisher_exact(cell_table, alternative="two-sided")
            pval = float(pval_f)
            test_method = "fisher_exact"
        else:
            # Pooled two-proportion z-test (B then A)
            _, pval_z = proportions_ztest(
                count=[xB, xA],
                nobs=[nB, nA],
                alternative="two-sided",
            )
            pval = float(pval_z)
            test_method = "z_test"

    return BinaryEffectResult(
        metric=metric_name,
        control=control_name,
        treatment=treatment_name,
        n_control=nA,
        n_treatment=nB,
        retained_control=xA,
        retained_treatment=xB,
        rate_control=pA,
        rate_treatment=pB,
        rate_control_ci=rate_control_ci,
        rate_treatment_ci=rate_treatment_ci,
        effect_absolute=delta,
        effect_percentage_points=delta_pp,
        relative_change_percent=rel_change,
        relative_change_unavailable_reason=rel_reason,
        ci_absolute=ci_absolute,
        confidence_level=1.0 - alpha,
        confidence_method=method,
        pvalue=pval,
        test_method=test_method,
        alternative="two-sided",
    )


def calculate_retention_effect(
    df: pd.DataFrame,
    metric_col: str = "retention_7",
    control_arm: str = "gate_30",
    treatment_arm: str = "gate_40",
    alpha: float = 0.05,
    method: str = "newcomb",
) -> BinaryEffectResult:
    """Extract counts from validated DataFrame and compute binary retention effect."""
    df_ctrl = df[df["version"] == control_arm]
    df_treat = df[df["version"] == treatment_arm]

    nA = len(df_ctrl)
    nB = len(df_treat)

    xA = int(df_ctrl[metric_col].sum())
    xB = int(df_treat[metric_col].sum())

    return calculate_binary_effect(
        xA=xA,
        nA=nA,
        xB=xB,
        nB=nB,
        metric_name=metric_col,
        control_name=control_arm,
        treatment_name=treatment_arm,
        alpha=alpha,
        method=method,
    )


def summarize_arm_engagement(series: pd.Series, arm_name: str) -> ArmEngagementSummary:
    """Compute full-data summary statistics for game rounds engagement."""
    arr = series.to_numpy(dtype=float)
    n = len(arr)
    if n == 0:
        raise ValueError(f"Empty series for arm {arm_name}")

    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    med_val = float(np.median(arr))
    zero_frac = float(np.mean(arr == 0))
    p95_val = float(np.percentile(arr, 95))
    p99_val = float(np.percentile(arr, 99))
    max_val = float(np.max(arr))

    return ArmEngagementSummary(
        arm=arm_name,
        n=n,
        mean=mean_val,
        std=std_val,
        median=med_val,
        zero_fraction=zero_frac,
        p95=p95_val,
        p99=p99_val,
        max=max_val,
    )


def calculate_engagement_analysis(
    df: pd.DataFrame,
    rounds_col: str = "sum_gamerounds",
    control_arm: str = "gate_30",
    treatment_arm: str = "gate_40",
) -> EngagementAnalysisResult:
    """Full-data engagement summaries and Welch's t-test."""
    ctrl_series = df[df["version"] == control_arm][rounds_col]
    treat_series = df[df["version"] == treatment_arm][rounds_col]

    sum_ctrl = summarize_arm_engagement(ctrl_series, control_arm)
    sum_treat = summarize_arm_engagement(treat_series, treatment_arm)

    mean_diff = sum_treat.mean - sum_ctrl.mean
    mean_diff_pct = (100.0 * mean_diff / sum_ctrl.mean) if sum_ctrl.mean > 0 else None

    # Welch's t-test (equal_var=False)
    if np.all(ctrl_series == ctrl_series.iloc[0]) and np.all(treat_series == treat_series.iloc[0]):
        if ctrl_series.iloc[0] == treat_series.iloc[0]:
            t_stat = 0.0
            p_val = 1.0
            test_method = "exact_constant"
        else:
            t_stat = 0.0
            p_val = 0.0
            test_method = "degenerate_constant"
    else:
        res = ttest_ind(treat_series, ctrl_series, equal_var=False)
        t_stat = float(res.statistic)
        p_val = float(res.pvalue)
        test_method = "welch_ttest"

    return EngagementAnalysisResult(
        metric=rounds_col,
        control_summary=sum_ctrl,
        treatment_summary=sum_treat,
        mean_diff_absolute=mean_diff,
        mean_diff_percent=mean_diff_pct,
        welch_t_stat=t_stat,
        welch_pvalue=p_val,
        test_method=test_method,
    )


def calculate_outlier_sensitivity(
    df: pd.DataFrame,
    rounds_col: str = "sum_gamerounds",
    control_arm: str = "gate_30",
    treatment_arm: str = "gate_40",
    cap_percentile: float = 99.0,
) -> OutlierSensitivityResult:
    """Descriptive sensitivity winsorizing engagement at pooled 99th percentile."""
    all_rounds = df[rounds_col].to_numpy(dtype=float)
    cap_val = float(np.percentile(all_rounds, cap_percentile))

    ctrl_rounds = df[df["version"] == control_arm][rounds_col].to_numpy(dtype=float)
    treat_rounds = df[df["version"] == treatment_arm][rounds_col].to_numpy(dtype=float)

    orig_mean_diff = float(np.mean(treat_rounds) - np.mean(ctrl_rounds))

    ctrl_capped_count = int(np.sum(ctrl_rounds > cap_val))
    treat_capped_count = int(np.sum(treat_rounds > cap_val))

    ctrl_capped = np.minimum(ctrl_rounds, cap_val)
    treat_capped = np.minimum(treat_rounds, cap_val)

    ctrl_mean_capped = float(np.mean(ctrl_capped))
    treat_mean_capped = float(np.mean(treat_capped))
    capped_mean_diff = float(treat_mean_capped - ctrl_mean_capped)

    return OutlierSensitivityResult(
        cap_percentile=cap_percentile,
        cap_value=cap_val,
        control_capped_count=ctrl_capped_count,
        treatment_capped_count=treat_capped_count,
        control_capped_mean=ctrl_mean_capped,
        treatment_capped_mean=treat_mean_capped,
        original_mean_diff=orig_mean_diff,
        capped_mean_diff=capped_mean_diff,
        notes=f"Engagement winsorized at pooled p{cap_percentile:.0f} ({cap_val:.1f} rounds). Descriptive sensitivity only.",
    )


def calculate_primary_bootstrap_sensitivity(
    df: pd.DataFrame,
    metric_col: str = "retention_7",
    control_arm: str = "gate_30",
    treatment_arm: str = "gate_40",
    replicates: int = 10000,
    seed: int = 42,
    alpha: float = 0.05,
) -> BootstrapSensitivityResult:
    """Compute bootstrap percentile confidence interval for binary difference using binomial draws."""
    ctrl_series = df[df["version"] == control_arm][metric_col]
    treat_series = df[df["version"] == treatment_arm][metric_col]

    nA = len(ctrl_series)
    nB = len(treat_series)
    xA = int(ctrl_series.sum())
    xB = int(treat_series.sum())

    pA = xA / nA
    pB = xB / nB
    orig_effect = pB - pA

    rng = np.random.default_rng(seed)
    boot_xA = rng.binomial(n=nA, p=pA, size=replicates)
    boot_xB = rng.binomial(n=nB, p=pB, size=replicates)

    boot_diffs = (boot_xB / nB) - (boot_xA / nA)

    lower_pct = 100.0 * (alpha / 2.0)
    upper_pct = 100.0 * (1.0 - alpha / 2.0)

    ci_low = float(np.percentile(boot_diffs, lower_pct))
    ci_high = float(np.percentile(boot_diffs, upper_pct))

    return BootstrapSensitivityResult(
        replicates=replicates,
        seed=seed,
        original_effect=orig_effect,
        bootstrap_ci_absolute=(ci_low, ci_high),
        bootstrap_ci_percentage_points=(100.0 * ci_low, 100.0 * ci_high),
        notes=f"{replicates:,} independent binomial bootstrap resamples (seed={seed}). Percentile interval.",
    )


def run_secondary_and_sensitivity_analysis(
    df: pd.DataFrame,
    control_arm: str = "gate_30",
    treatment_arm: str = "gate_40",
    alpha: float = 0.05,
    method: str = "newcomb",
    seed: int = 42,
    bootstrap_replicates: int = 10000,
) -> SecondaryAnalysisResult:
    """Run full secondary, engagement, Holm-Bonferroni correction, and sensitivity suite."""
    # 1. Day-1 retention
    day1_res = calculate_retention_effect(
        df=df,
        metric_col="retention_1",
        control_arm=control_arm,
        treatment_arm=treatment_arm,
        alpha=alpha,
        method=method,
    )

    # 2. Engagement analysis
    eng_res = calculate_engagement_analysis(
        df=df,
        rounds_col="sum_gamerounds",
        control_arm=control_arm,
        treatment_arm=treatment_arm,
    )

    # 3. Holm-Bonferroni correction for exploratory family (day-1 retention, engagement Welch)
    raw_pvals = [day1_res.pvalue, eng_res.welch_pvalue]
    _, adj_pvals, _, _ = multipletests(raw_pvals, alpha=alpha, method="holm")

    holm_pvals = {
        "retention_1_raw": float(raw_pvals[0]),
        "retention_1_holm": float(adj_pvals[0]),
        "sum_gamerounds_raw": float(raw_pvals[1]),
        "sum_gamerounds_holm": float(adj_pvals[1]),
    }

    # 4. Outlier sensitivity at pooled p99
    outlier_sens = calculate_outlier_sensitivity(
        df=df,
        rounds_col="sum_gamerounds",
        control_arm=control_arm,
        treatment_arm=treatment_arm,
        cap_percentile=99.0,
    )

    # 5. Bootstrap sensitivity for primary endpoint
    boot_sens = calculate_primary_bootstrap_sensitivity(
        df=df,
        metric_col="retention_7",
        control_arm=control_arm,
        treatment_arm=treatment_arm,
        replicates=bootstrap_replicates,
        seed=seed,
        alpha=alpha,
    )

    return SecondaryAnalysisResult(
        day1_retention=day1_res,
        engagement=eng_res,
        holm_family_pvalues=holm_pvals,
        outlier_sensitivity=outlier_sens,
        primary_bootstrap=boot_sens,
    )
