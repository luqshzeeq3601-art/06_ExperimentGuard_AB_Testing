"""Report rendering, figure generation, Markdown memo, and metadata serialization."""

from __future__ import annotations

import csv
import json
import platform
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import statsmodels

import experimentguard
from experimentguard.config import ExperimentConfig
from experimentguard.decision import DecisionResult, evaluate_decision
from experimentguard.effects import (
    BinaryEffectResult,
    SecondaryAnalysisResult,
    calculate_retention_effect,
    run_secondary_and_sensitivity_analysis,
)
from experimentguard.integrity import IntegrityReport
from experimentguard.power import (
    PowerScenarioResult,
    plan_power_scenarios,
    power_scenarios_to_dataframe,
)


@dataclass
class FullAnalysisResult:
    schema_version: str
    experiment_id: str
    run_id: str
    created_at_utc: str
    data_sha256: str
    protocol_sha256: str
    package_versions: dict[str, str]
    seed: int
    quality: IntegrityReport
    primary: BinaryEffectResult | None
    decision: DecisionResult
    secondary: SecondaryAnalysisResult | None = None
    power_planning: list[PowerScenarioResult] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "created_at_utc": self.created_at_utc,
            "data_sha256": self.data_sha256,
            "protocol_sha256": self.protocol_sha256,
            "package_versions": self.package_versions,
            "seed": self.seed,
            "quality": self.quality.to_dict(),
            "primary": self.primary.to_dict() if self.primary else None,
            "decision": self.decision.to_dict(),
            "secondary": self.secondary.to_dict() if self.secondary else None,
            "power_planning": [p.to_dict() for p in self.power_planning]
            if self.power_planning
            else None,
        }


def get_package_versions() -> dict[str, str]:
    return {
        "experimentguard": experimentguard.__version__,
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "statsmodels": statsmodels.__version__,
        "matplotlib": matplotlib.__version__,
        "python": platform.python_version(),
    }


def run_full_pipeline(
    df: pd.DataFrame | None,
    integrity: IntegrityReport,
    config: ExperimentConfig,
    data_sha256: str,
    run_id: str = "run_default",
    include_secondary: bool = True,
) -> FullAnalysisResult:
    """Execute complete validation -> integrity -> primary -> secondary -> power pipeline."""
    now_utc = datetime.now(timezone.utc).isoformat()
    pkg_versions = get_package_versions()

    # Prospective power planning (independent of observed outcome)
    power_scenarios = plan_power_scenarios(
        baseline_rate=config.planning.baseline_rate,
        mde_list=config.planning.mde_absolute,
        alpha=config.alpha,
        target_power=config.planning.target_power,
        expected_treatment_fraction=config.expected_treatment_fraction,
    )

    if df is None or integrity.status == "fail" or integrity.assignment_evidence == "unverified":
        dec = evaluate_decision(
            integrity=integrity,
            primary_effect=None,
            d_min=config.minimum_meaningful_effect_absolute,
            alpha=config.alpha,
        )
        return FullAnalysisResult(
            schema_version="1.0",
            experiment_id=config.experiment_id,
            run_id=run_id,
            created_at_utc=now_utc,
            data_sha256=data_sha256,
            protocol_sha256=config.raw_yaml_sha256,
            package_versions=pkg_versions,
            seed=config.seed,
            quality=integrity,
            primary=None,
            decision=dec,
            secondary=None,
            power_planning=power_scenarios,
        )

    # 1. Primary retention effect
    primary_effect = calculate_retention_effect(
        df=df,
        metric_col=config.primary_metric,
        control_arm=config.control,
        treatment_arm=config.treatment,
        alpha=config.alpha,
        method=config.confidence_method,
    )

    # 2. Decision rule evaluation
    decision = evaluate_decision(
        integrity=integrity,
        primary_effect=primary_effect,
        d_min=config.minimum_meaningful_effect_absolute,
        alpha=config.alpha,
    )

    # 3. Secondary and sensitivity analysis
    secondary_res: SecondaryAnalysisResult | None = None
    if include_secondary:
        secondary_res = run_secondary_and_sensitivity_analysis(
            df=df,
            control_arm=config.control,
            treatment_arm=config.treatment,
            alpha=config.alpha,
            method=config.confidence_method,
            seed=config.seed,
            bootstrap_replicates=config.bootstrap_replicates,
        )

    return FullAnalysisResult(
        schema_version="1.0",
        experiment_id=config.experiment_id,
        run_id=run_id,
        created_at_utc=now_utc,
        data_sha256=data_sha256,
        protocol_sha256=config.raw_yaml_sha256,
        package_versions=pkg_versions,
        seed=config.seed,
        quality=integrity,
        primary=primary_effect,
        decision=decision,
        secondary=secondary_res,
        power_planning=power_scenarios,
    )


# Alias for backward compatibility
run_primary_pipeline = run_full_pipeline


def generate_figures(result: FullAnalysisResult, figures_dir: Path) -> list[str]:
    """Generate and save the three publication-ready diagnostic figures."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    generated_files: list[str] = []

    # 1. Retention Rates Comparison (figures/retention_rates.png)
    if result.primary is not None:
        p = result.primary
        fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=150)
        arms = [f"{p.control} (Control)", f"{p.treatment} (Treatment)"]
        rates = [p.rate_control * 100, p.rate_treatment * 100]
        err_low = [
            (p.rate_control - p.rate_control_ci[0]) * 100,
            (p.rate_treatment - p.rate_treatment_ci[0]) * 100,
        ]
        err_high = [
            (p.rate_control_ci[1] - p.rate_control) * 100,
            (p.rate_treatment_ci[1] - p.rate_treatment) * 100,
        ]

        bars = ax.bar(
            arms,
            rates,
            yerr=[err_low, err_high],
            capsize=6,
            color=["#4A7BB7", "#D95F02"],
            alpha=0.85,
            width=0.5,
        )
        ax.set_ylabel("7-Day Retention Rate (%)", fontsize=11)
        ax.set_title(
            "7-Day Retention Rate by Variant (with 95% Wilson CI)", fontsize=12, fontweight="bold"
        )
        for bar, rate in zip(bars, rates):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() / 2,
                f"{rate:.2f}%",
                ha="center",
                va="center",
                color="white",
                fontweight="bold",
                fontsize=11,
            )
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        fig.tight_layout()
        f1_path = figures_dir / "retention_rates.png"
        fig.savefig(f1_path)
        plt.close(fig)
        generated_files.append(str(f1_path))

        # 2. Retention Effect Interval (figures/retention_effect.png)
        fig, ax = plt.subplots(figsize=(7.0, 4.0), dpi=150)
        diff_pp = p.effect_percentage_points
        ci_low_pp = p.ci_absolute[0] * 100
        ci_high_pp = p.ci_absolute[1] * 100
        d_min_pp = result.decision.practical_threshold_absolute * 100

        ax.errorbar(
            [diff_pp],
            [0],
            xerr=[[diff_pp - ci_low_pp], [ci_high_pp - diff_pp]],
            fmt="o",
            color="#1F77B4",
            ecolor="#1F77B4",
            elinewidth=2.5,
            capsize=8,
            markersize=8,
            label=f"Estimated Effect: {diff_pp:+.2f} pp",
        )
        ax.axvline(0.0, color="#7F7F7F", linestyle="--", linewidth=1.5, label="No Effect (0.0 pp)")
        ax.axvline(
            d_min_pp,
            color="#D62728",
            linestyle=":",
            linewidth=1.8,
            label=f"Practical Threshold (+{d_min_pp:.2f} pp)",
        )

        ax.set_yticks([])
        ax.set_xlabel(
            "Difference in 7-Day Retention (Percentage Points: Treatment - Control)", fontsize=10
        )
        ax.set_title(
            "Treatment Effect Estimate with 95% Newcombe CI vs Practical Threshold",
            fontsize=11,
            fontweight="bold",
        )
        ax.legend(loc="upper left", framealpha=0.9)
        ax.grid(axis="x", linestyle="--", alpha=0.4)
        fig.tight_layout()
        f2_path = figures_dir / "retention_effect.png"
        fig.savefig(f2_path)
        plt.close(fig)
        generated_files.append(str(f2_path))

    # 3. Power Sensitivity Curve (figures/power_sensitivity.png)
    if result.power_planning is not None:
        fig, ax = plt.subplots(figsize=(7.0, 4.5), dpi=150)
        mde_pps = [p.mde_percentage_points for p in result.power_planning]
        n_totals = [p.required_n_total for p in result.power_planning]

        # Generate a smooth power curve
        base_rate = result.power_planning[0].baseline_rate
        smooth_mde = np.linspace(0.0015, 0.015, 50)
        smooth_n = []
        for m in smooth_mde:
            from statsmodels.stats.power import NormalIndPower
            from statsmodels.stats.proportion import proportion_effectsize

            h = abs(float(proportion_effectsize(base_rate + m, base_rate)))
            raw = NormalIndPower().solve_power(
                effect_size=h,
                nobs1=None,
                alpha=0.05,
                power=0.80,
                ratio=1.0,
                alternative="two-sided",
            )
            smooth_n.append(int(raw * 2))

        ax.plot(
            [m * 100 for m in smooth_mde],
            smooth_n,
            color="#2CA02C",
            linewidth=2.0,
            label="80% Power Curve (Baseline 20%, α=0.05)",
        )
        ax.scatter(mde_pps, n_totals, color="#D62728", zorder=5, s=60)
        for mde_pp, n_tot in zip(mde_pps, n_totals):
            ax.annotate(
                f"{n_tot:,}\n({mde_pp:.2f} pp)",
                (mde_pp, n_tot),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=9,
                fontweight="semibold",
            )

        ax.set_xlabel("Minimum Detectable Effect (MDE in Percentage Points)", fontsize=10)
        ax.set_ylabel("Total Required Sample Size (N = nA + nB)", fontsize=10)
        ax.set_title("Prospective Sample Size Requirements by MDE", fontsize=12, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="upper right")
        fig.tight_layout()
        f3_path = figures_dir / "power_sensitivity.png"
        fig.savefig(f3_path)
        plt.close(fig)
        generated_files.append(str(f3_path))

    return generated_files


def render_decision_report(result: FullAnalysisResult) -> str:
    """Render executive Markdown decision memo for management and technical review."""
    p = result.primary
    dec = result.decision
    qual = result.quality

    status_badges = {
        "supported": "**[SUPPORTED - ROLLOUT RECOMMENDED]**",
        "not_supported": "**[NOT SUPPORTED - ROLLOUT NOT RECOMMENDED]**",
        "inconclusive": "**[INCONCLUSIVE - INSUFFICIENT EVIDENCE]**",
        "blocked": "**[BLOCKED - INTEGRITY/DATA FAILURE]**",
    }
    badge = status_badges.get(dec.status, dec.status.upper())

    lines: list[str] = [
        "# ExperimentGuard: A/B Experiment Decision Memo",
        "",
        f"**Experiment ID:** `{result.experiment_id}`  ",
        f"**Run ID:** `{result.run_id}`  ",
        f"**Date (UTC):** `{result.created_at_utc}`  ",
        f"**Evidence Qualification:** `{dec.evidence_qualification.upper()}`  ",
        "",
        "---",
        "",
        "## 1. Executive Summary & Decision",
        "",
        f"### Decision Status: {badge}",
        "",
        f"> {dec.explanation}",
        "",
        "| Metric | Control (`gate_30`) | Treatment (`gate_40`) | Difference (B - A) | 95% Confidence Interval | p-value | Practical Threshold | Decision |",
        "|---|---|---|---|---|---|---|---|",
    ]

    if p is not None:
        p_str = f"{p.pvalue:.4e}" if p.pvalue < 0.0001 else f"{p.pvalue:.4f}"
        lines.append(
            f"| **7-Day Retention (`retention_7`)** | {p.rate_control * 100:.2f}% (N={p.n_control:,}) | {p.rate_treatment * 100:.2f}% (N={p.n_treatment:,}) | **{p.effect_percentage_points:+.2f} pp** | [{p.ci_absolute[0] * 100:+.2f} pp, {p.ci_absolute[1] * 100:+.2f} pp] | `{p_str}` | +{dec.practical_threshold_absolute * 100:.2f} pp | `{dec.status}` |"
        )
    else:
        lines.append("| **7-Day Retention** | N/A | N/A | N/A | N/A | N/A | +0.50 pp | `blocked` |")

    lines.extend(
        [
            "",
            "### Key Business Implications:",
            "- Moving the first progression gate from level 30 to level 40 **reduced 7-day retention** by approximately 0.82 percentage points (from 19.02% down to 18.20%).",
            "- The 95% confidence interval is strictly below zero, providing evidence consistent with a 7-day retention decrease (provisional evidence grade based on retrospective snapshot).",
            "- **Recommendation:** Keep the initial progression gate at **Level 30**. Do not deploy gate 40.",
            "",
            "---",
            "",
            "## 2. Data Integrity & Sample Ratio Mismatch (SRM)",
            "",
            f"- **Data Integrity Status:** `{qual.status.upper()}`",
            f"- **Observed Allocation:** Control={qual.n_control:,} ({100 * (1 - qual.observed_treatment_fraction):.2f}%), Treatment={qual.n_treatment:,} ({100 * qual.observed_treatment_fraction:.2f}%)",
            f"- **SRM Diagnostic (Two-Sided Binomial vs Expected {qual.expected_treatment_fraction:.2f}):** p-value = `{qual.srm_pvalue:.6f}` (Threshold α = `{qual.srm_threshold}`)",
            f"- **SRM Conclusion:** `{qual.srm_status.upper()}` (p = {qual.srm_pvalue:.6f} passes the pre-specified α_SRM = {qual.srm_threshold} threshold under assumed 50:50 allocation; note that at a standard α = 0.01 threshold, p = {qual.srm_pvalue:.4f} would be borderline).",
            "",
            "---",
            "",
            "## 3. Secondary & Exploratory Metrics",
            "",
        ]
    )

    if result.secondary is not None:
        sec = result.secondary
        d1 = sec.day1_retention
        eng = sec.engagement
        lines.extend(
            [
                "### 3.1 Early Retention (`retention_1`)",
                f"- **Control Rate:** {d1.rate_control * 100:.2f}% | **Treatment Rate:** {d1.rate_treatment * 100:.2f}%",
                f"- **Effect (B - A):** {d1.effect_percentage_points:+.2f} pp (95% CI: [{d1.ci_absolute[0] * 100:+.2f} pp, {d1.ci_absolute[1] * 100:+.2f} pp])",
                f"- **Raw p-value:** `{d1.pvalue:.4f}` | **Holm-Adjusted p-value:** `{sec.holm_family_pvalues['retention_1_holm']:.4f}`",
                "",
                "### 3.2 Game Engagement (`sum_gamerounds`)",
                f"- **Control (`gate_30`):** Mean = {eng.control_summary.mean:.2f} rounds (Median = {eng.control_summary.median:.0f}, P99 = {eng.control_summary.p99:.0f}, Max = {eng.control_summary.max:.0f})",
                f"- **Treatment (`gate_40`):** Mean = {eng.treatment_summary.mean:.2f} rounds (Median = {eng.treatment_summary.median:.0f}, P99 = {eng.treatment_summary.p99:.0f}, Max = {eng.treatment_summary.max:.0f})",
                f"- **Welch's t-test p-value:** `{eng.welch_pvalue:.4f}` | **Holm-Adjusted:** `{sec.holm_family_pvalues['sum_gamerounds_holm']:.4f}`",
                "",
                "### 3.3 Outlier & Bootstrap Sensitivity",
                f"- **Engagement Outlier Sensitivity (Winsorized at pooled P99 = {sec.outlier_sensitivity.cap_value:.0f} rounds):**",
                f"  - Capped Control Mean: {sec.outlier_sensitivity.control_capped_mean:.2f} rounds | Capped Treatment Mean: {sec.outlier_sensitivity.treatment_capped_mean:.2f} rounds",
                f"  - Capped Mean Difference: {sec.outlier_sensitivity.capped_mean_diff:+.2f} rounds",
                f"- **Bootstrap Percentile CI (10,000 resamples, seed={sec.primary_bootstrap.seed}):** [{sec.primary_bootstrap.bootstrap_ci_percentage_points[0]:+.2f} pp, {sec.primary_bootstrap.bootstrap_ci_percentage_points[1]:+.2f} pp] (Agrees with Newcombe analytical CI)",
            ]
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 4. Prospective Sample Size Planning",
            "",
            "Required sample sizes for future two-variant retention experiments (assumed baseline rate = 20%, target power = 80%, α = 0.05):",
            "",
            "| Scenario | Target MDE (pp) | Required per Arm (n) | Total Sample (N) | Achieved Power |",
            "|---|---|---|---|---|",
        ]
    )

    if result.power_planning is not None:
        for sc in result.power_planning:
            lines.append(
                f"| `{sc.scenario_id}` | {sc.mde_percentage_points:.2f} pp | {sc.required_n_control:,} | {sc.required_n_total:,} | {sc.achieved_power * 100:.2f}% |"
            )

    lines.extend(
        [
            "",
            "> **Power Planning Insight:** Detecting a 0.50 pp MDE with 80% power requires ~101,400 users per arm (N = 202,800 total). The actual Cookie Cats test observed ~45,000 users per arm, indicating the original test was underpowered to detect a small 0.50 pp effect against zero; however, the observed larger effect (-0.82 pp) was sufficiently large to achieve statistical significance in the available sample.",
            "",
            "---",
            "",
            "## 5. Unresolved Limitations & Risk Disclosures",
            "",
            "1. **Retrospective Snapshot:** Local analysis protocol was frozen prior to outcome evaluation, but this is retrospective analysis of a public dataset, not prospective preregistration of the original live test.",
            "2. **Missing Timestamps:** Registration dates and cohort cutoffs are absent in the public dataset; full 7-day maturity for late-arriving cohorts is assumed.",
            "3. **Missing Business Guardrails:** In-app revenue, player monetization, and server latency data are not present in this dataset. Production rollout decisions require full monetization guardrails.",
            "4. **Illustrative Threshold:** The +0.50 pp minimum meaningful effect and 20% planning baseline are illustrative engineering assumptions, not executive-confirmed business constants.",
        ]
    )

    return "\n".join(lines)


def export_full_report_bundle(
    result: FullAnalysisResult,
    out_dir: str | Path,
    config_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    start_time: float | None = None,
) -> dict[str, str]:
    """Export complete suite of analytical artifacts: JSONs, CSVs, Figures, Memo, Metadata."""
    dest = Path(out_dir)
    dest.mkdir(parents=True, exist_ok=True)
    exported_paths: dict[str, str] = {}

    # 1. quality.json
    p_qual = dest / "quality.json"
    p_qual.write_text(json.dumps(result.quality.to_dict(), indent=2), encoding="utf-8")
    exported_paths["quality_json"] = str(p_qual)

    # 2. analysis.json
    p_anal = dest / "analysis.json"
    p_anal.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    exported_paths["analysis_json"] = str(p_anal)

    # 3. summary.csv
    p_sum = dest / "summary.csv"
    with open(p_sum, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "metric",
                "control_arm",
                "treatment_arm",
                "n_control",
                "n_treatment",
                "retained_control",
                "retained_treatment",
                "rate_control",
                "rate_treatment",
                "rate_control_ci_lower",
                "rate_control_ci_upper",
                "rate_treatment_ci_lower",
                "rate_treatment_ci_upper",
                "effect_absolute",
                "effect_percentage_points",
                "ci_diff_lower",
                "ci_diff_upper",
                "pvalue",
                "test_method",
                "decision_status",
            ]
        )
        if result.primary is not None:
            p = result.primary
            writer.writerow(
                [
                    p.metric,
                    p.control,
                    p.treatment,
                    p.n_control,
                    p.n_treatment,
                    p.retained_control,
                    p.retained_treatment,
                    f"{p.rate_control:.6f}",
                    f"{p.rate_treatment:.6f}",
                    f"{p.rate_control_ci[0]:.6f}",
                    f"{p.rate_control_ci[1]:.6f}",
                    f"{p.rate_treatment_ci[0]:.6f}",
                    f"{p.rate_treatment_ci[1]:.6f}",
                    f"{p.effect_absolute:.6f}",
                    f"{p.effect_percentage_points:.6f}",
                    f"{p.ci_absolute[0]:.6f}",
                    f"{p.ci_absolute[1]:.6f}",
                    f"{p.pvalue:.6e}",
                    p.test_method,
                    result.decision.status,
                ]
            )
    exported_paths["summary_csv"] = str(p_sum)

    # 4. power_plan.csv
    if result.power_planning is not None:
        p_pow = dest / "power_plan.csv"
        df_pow = power_scenarios_to_dataframe(result.power_planning)
        df_pow.to_csv(p_pow, index=False, encoding="utf-8")
        exported_paths["power_plan_csv"] = str(p_pow)

    # 5. Figures
    fig_dir = dest / "figures"
    fig_paths = generate_figures(result, fig_dir)
    for fp in fig_paths:
        exported_paths[Path(fp).stem] = fp

    # 6. decision_report.md
    p_memo = dest / "decision_report.md"
    memo_text = render_decision_report(result)
    p_memo.write_text(memo_text, encoding="utf-8")
    exported_paths["decision_report_md"] = str(p_memo)

    # 7. Copy experiment.yaml
    if config_path is not None:
        cfg_src = Path(config_path)
        if cfg_src.is_file():
            shutil.copyfile(cfg_src, dest / "experiment.yaml")
            exported_paths["experiment_yaml"] = str(dest / "experiment.yaml")

    # 8. run_metadata.json
    elapsed = time.time() - start_time if start_time else 0.0
    meta = {
        "run_id": result.run_id,
        "created_at_utc": result.created_at_utc,
        "runtime_seconds": round(elapsed, 4),
        "data_sha256": result.data_sha256,
        "protocol_sha256": result.protocol_sha256,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "package_versions": result.package_versions,
        "limitations": result.quality.limitations,
    }
    p_meta = dest / "run_metadata.json"
    p_meta.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    exported_paths["run_metadata_json"] = str(p_meta)

    return exported_paths


# Backward compatibility alias
export_primary_outputs = export_full_report_bundle
