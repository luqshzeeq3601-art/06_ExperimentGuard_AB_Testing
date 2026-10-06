"""ExperimentGuard: Interactive A/B Experiment Analysis and Power Planning Dashboard."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import experimentguard
from experimentguard.config import ExperimentConfig
from experimentguard.data import validate_dataframe
from experimentguard.decision import evaluate_decision
from experimentguard.effects import calculate_retention_effect
from experimentguard.integrity import check_integrity
from experimentguard.power import (
    plan_power_scenarios,
    plan_sample_size_scenario,
    power_scenarios_to_dataframe,
)

# Set page configuration
st.set_page_config(
    page_title="ExperimentGuard - A/B Testing & Power Planning",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for executive cards and styling
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-title {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #0F172A;
        font-size: 1.6rem;
        font-weight: 700;
    }
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-harm {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        display: inline-block;
    }
    .badge-pass {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_cookie_cats_cached_results() -> dict:
    """Load production cookie-cats-v1 analysis JSON if present."""
    report_file = (
        Path(__file__).resolve().parent.parent / "reports" / "cookie-cats-v1" / "analysis.json"
    )
    if report_file.exists():
        with open(report_file, encoding="utf-8") as f:
            return json.load(f)
    return {}


# Sidebar Branding & Navigation
with st.sidebar:
    st.title("🛡️ ExperimentGuard")
    st.caption(f"v{experimentguard.__version__} | Experiment Analysis Engine")
    st.markdown("---")
    st.markdown(
        """
        **ExperimentGuard** enforces reproducible, leak-free experimentation:
        - Exact Sample Ratio Mismatch (SRM)
        - Wilson score & Newcombe difference CIs
        - Deterministic four-status decision rules
        - Prospective sample size power solver
        """
    )
    st.markdown("---")
    st.markdown("### Protocol Specifications")
    st.markdown(
        """
        - **Primary Endpoint:** 7-Day Retention (`retention_7`)
        - **Decision Alpha:** `0.05` (two-sided)
        - **SRM Alpha:** `0.001` (two-sided exact binomial)
        - **Practical Threshold ($d_{min}$):** `+0.50 pp`
        """
    )
    st.markdown("---")
    st.markdown(
        "[GitHub Repository](https://github.com/luqshzeeq3601-art/06_ExperimentGuard_AB_Testing)  \n"
        "[Documentation & Protocol](https://github.com/luqshzeeq3601-art/06_ExperimentGuard_AB_Testing/tree/main/docs)"
    )


# Header
st.title("A/B Experiment Analysis & Prospective Power Planning")
st.markdown(
    "Rigorous statistical evaluation of experimentation data, diagnostic integrity checks, "
    "and prospective sample size determination."
)

tab1, tab2, tab3 = st.tabs(
    [
        "📊 Case Study: Cookie Cats",
        "🎯 Prospective Power Simulator",
        "🧪 Live A/B Evaluator (Upload CSV)",
    ]
)

# ==============================================================================
# TAB 1: COOKIE CATS CASE STUDY
# ==============================================================================
with tab1:
    st.subheader("Cookie Cats: First Progression Gate Placement Analysis")
    st.markdown(
        "**Business Question:** *Does moving the initial progression gate from Level 30 (`gate_30`) "
        "to Level 40 (`gate_40`) improve 7-day player retention?*"
    )

    data = get_cookie_cats_cached_results()

    # Top KPI Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Control (Gate 30)</div>
                <div class="metric-value">19.02%</div>
                <div class="metric-delta" style="color: #64748B;">N = 44,700 users</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Treatment (Gate 40)</div>
                <div class="metric-value">18.20%</div>
                <div class="metric-delta" style="color: #64748B;">N = 45,489 users</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Difference (B - A)</div>
                <div class="metric-value" style="color: #DC2626;">-0.82 pp</div>
                <div class="metric-delta" style="color: #DC2626;">-4.31% Relative Change</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Protocol Decision</div>
                <div class="metric-value"><span class="badge-harm">NOT SUPPORTED</span></div>
                <div class="metric-delta" style="color: #DC2626;">Evidence of Harm (U &lt; 0)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed Statistical Results
    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown("### Primary Inference & Decision")
        st.markdown(
            """
            | Parameter | Value | Interpretation |
            |---|---|---|
            | **Observed Effect** | **-0.8201 percentage points** | Statistically significant drop in retention |
            | **95% Newcombe CI** | **[-1.3340 pp, -0.3063 pp]** | Upper bound strictly below 0.0 (Harm detected) |
            | **Two-Sided z-test p-value** | **`0.001554`** | Statistically significant ($p < 0.05$) |
            | **Practical Threshold ($d_{min}$)** | **+0.50 pp** | Minimum meaningful uplift required for rollout |
            | **SRM Diagnostic** | **`PASS` ($p = 0.00869$)** | Above pre-specified $\\alpha=0.001$; borderline at $\\alpha=0.01$ |
            | **Evidence Grade** | **`PROVISIONAL`** | Retrospective analysis of public snapshot |
            """
        )

        st.info(
            "**Business Recommendation:** Retain the first progression gate at **Level 30**. "
            "Gate 40 creates a statistically detectable reduction in 7-day player retention (-4.31% relative drop)."
        )

    with c_right:
        st.markdown("### Primary Effect Visualization")
        fig, ax = plt.subplots(figsize=(6, 4))
        effects = [-0.8201]
        ci_lower = [-1.3340]
        ci_upper = [-0.3063]
        d_min = 0.50

        y_pos = [0]
        ax.errorbar(
            effects,
            y_pos,
            xerr=[
                [effects[0] - ci_lower[0]],
                [ci_upper[0] - effects[0]],
            ],
            fmt="o",
            color="#DC2626",
            ecolor="#DC2626",
            elinewidth=2.5,
            capsize=6,
            markersize=8,
            label="Observed Effect & 95% Newcombe CI",
        )
        ax.axvline(
            0,
            color="#475569",
            linestyle="--",
            linewidth=1.2,
            label="Zero Effect (No Change)",
        )
        ax.axvline(
            d_min,
            color="#2563EB",
            linestyle="-.",
            linewidth=1.5,
            label="Practical Threshold (+0.50 pp)",
        )
        ax.axvspan(-2.0, 0, color="#FEE2E2", alpha=0.3, label="Harm Zone (U < 0)")
        ax.axvspan(
            d_min,
            2.0,
            color="#DCFCE7",
            alpha=0.3,
            label="Support Zone (L > d_min)",
        )

        ax.set_xlim(-2.0, 1.5)
        ax.set_yticks([])
        ax.set_xlabel("7-Day Retention Difference (percentage points)")
        ax.set_title("Treatment Effect vs Decision Boundaries")
        ax.legend(loc="lower left", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.markdown("---")

    # Secondary Metrics & Sensitivity
    st.markdown("### Secondary Metrics & Sensitivity Analysis")
    col_sec1, col_sec2, col_sec3 = st.columns(3)
    with col_sec1:
        st.markdown("#### 1-Day Retention (`retention_1`)")
        st.write("- **Control:** 44.82% (N=44,700)")
        st.write("- **Treatment:** 44.23% (N=45,489)")
        st.write("- **Difference:** -0.59 pp (95% CI: [-1.24, +0.06])")
        st.write("- **Holm-Adjusted p-value:** `0.1488` (Not significant)")

    with col_sec2:
        st.markdown("#### Engagement (`sum_gamerounds`)")
        st.write("- **Control Mean:** 52.46 rounds (std=256.7)")
        st.write("- **Treatment Mean:** 51.30 rounds (std=103.3)")
        st.write("- **Mean Diff:** -1.16 rounds (Welch calc CI: [-3.73, +1.41])")
        st.write("- **Holm-Adjusted p-value:** `0.3759` (Not significant)")

    with col_sec3:
        st.markdown("#### Robustness & Sensitivity")
        st.write("- **P99 Winsorized Means:** 49.14 vs 48.85 rounds")
        st.write("- **Capped Diff:** -0.28 rounds (Descriptive check)")
        st.write("- **10k Bootstrap Retention CI:** [-1.34 pp, -0.31 pp]")
        st.write("- **Bootstrap Agreement:** Exactly confirms analytical Newcombe interval.")

# ==============================================================================
# TAB 2: PROSPECTIVE POWER SIMULATOR
# ==============================================================================
with tab2:
    st.subheader("Prospective Sample Size & Power Planning Simulator")
    st.markdown(
        "Determine required sample sizes for future retention A/B tests using Cohen's $h$ "
        "and normal approximation for two independent proportions."
    )

    c_sim_left, c_sim_right = st.columns([1, 2])

    with c_sim_left:
        st.markdown("#### Planning Parameters")
        p_base = st.slider(
            "Baseline Retention Rate (%)",
            min_value=5.0,
            max_value=50.0,
            value=20.0,
            step=1.0,
        )
        mde_input = st.slider(
            "Minimum Detectable Effect (MDE in pp)",
            min_value=0.10,
            max_value=3.00,
            value=0.50,
            step=0.05,
        )
        alpha_val = st.selectbox("Significance Level (α)", options=[0.01, 0.05, 0.10], index=1)
        power_val = st.slider(
            "Target Statistical Power (1 - β)",
            min_value=0.70,
            max_value=0.99,
            value=0.80,
            step=0.05,
        )
        alloc_ratio = st.slider(
            "Treatment Allocation Ratio (r = N_treatment / N_control)",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
        )

        # Calculate requirements
        p0 = p_base / 100.0
        mde_abs = mde_input / 100.0
        scenario = plan_sample_size_scenario(
            scenario_id="custom_simulator",
            baseline_rate=p0,
            mde_absolute=mde_abs,
            alpha=alpha_val,
            target_power=power_val,
            expected_treatment_fraction=alloc_ratio / (1.0 + alloc_ratio),
        )

        st.markdown("---")
        st.markdown("#### Required Sample Size")
        st.metric("Total Required Users (N)", f"{scenario.required_n_total:,}")
        st.metric(
            "Per Arm (Control / Treatment)",
            f"{scenario.required_n_control:,} / {scenario.required_n_treatment:,}",
        )
        st.caption(f"Achieved Power: {scenario.achieved_power * 100:.2f}%")

    with c_sim_right:
        st.markdown("#### Sensitivity Curve: Sample Size vs MDE")

        mde_range = np.linspace(0.15, 2.0, 30)
        n_totals = []
        for mde_i in mde_range:
            sc_i = plan_sample_size_scenario(
                scenario_id="curve",
                baseline_rate=p0,
                mde_absolute=mde_i / 100.0,
                alpha=alpha_val,
                target_power=power_val,
                expected_treatment_fraction=alloc_ratio / (1.0 + alloc_ratio),
            )
            n_totals.append(sc_i.required_n_total)

        fig_pow, ax_pow = plt.subplots(figsize=(7, 4.2))
        ax_pow.plot(mde_range, n_totals, color="#2563EB", linewidth=2.5, label="Total N")
        ax_pow.scatter(
            [mde_input],
            [scenario.required_n_total],
            color="#DC2626",
            s=80,
            zorder=5,
            label=f"Selected MDE ({mde_input:.2f} pp): {scenario.required_n_total:,} users",
        )
        ax_pow.set_xlabel("Minimum Detectable Effect (percentage points)", fontsize=10)
        ax_pow.set_ylabel("Total Required Sample Size (N)", fontsize=10)
        ax_pow.set_title(
            f"Power Curve (Baseline={p_base:.1f}%, Power={power_val * 100:.0f}%, α={alpha_val})",
            fontsize=11,
        )
        ax_pow.grid(True, linestyle="--", alpha=0.5)
        ax_pow.legend(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig_pow)
        plt.close(fig_pow)

        # Standard Protocol Pre-set Table
        st.markdown("#### Standard Protocol Planning Scenarios")
        std_scenarios = plan_power_scenarios()
        df_std = power_scenarios_to_dataframe(std_scenarios)
        st.dataframe(
            df_std[
                [
                    "scenario_id",
                    "mde_percentage_points",
                    "required_n_control",
                    "required_n_treatment",
                    "required_n_total",
                    "achieved_power",
                ]
            ],
            use_container_width=True,
        )

# ==============================================================================
# TAB 3: LIVE A/B EVALUATOR
# ==============================================================================
with tab3:
    st.subheader("Live A/B Evaluator (Upload CSV or Test Fixture)")
    st.markdown(
        "Upload a custom experimentation dataset to execute the full ExperimentGuard engine: "
        "Strict ITT validation, SRM test, Newcombe intervals, and decision rule evaluation."
    )

    col_up, col_param = st.columns([2, 1])

    with col_param:
        st.markdown("#### Protocol Parameters")
        d_min_custom = (
            st.number_input(
                "Practical Threshold d_min (pp)",
                value=0.50,
                step=0.05,
                format="%.2f",
            )
            / 100.0
        )
        alpha_custom = st.selectbox(
            "Decision Alpha (α)", options=[0.01, 0.05, 0.10], index=1, key="a_c"
        )
        srm_alpha_custom = st.number_input("SRM Alpha Threshold", value=0.001, format="%.4f")

    with col_up:
        uploaded_file = st.file_uploader(
            "Upload Experiment CSV (Required columns: userid, version, sum_gamerounds, retention_1, retention_7)",
            type=["csv"],
        )

        use_demo = st.checkbox("Or use built-in synthetic test fixture", value=False)

    df_to_analyze: pd.DataFrame | None = None

    if uploaded_file is not None:
        try:
            df_to_analyze = pd.read_csv(uploaded_file)
            st.success(f"Loaded `{uploaded_file.name}` ({len(df_to_analyze):,} rows)")
        except Exception as e:
            st.error(f"Error parsing CSV: {e}")
    elif use_demo:
        fixture_path = (
            Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "valid_experiment.csv"
        )
        if fixture_path.exists():
            df_to_analyze = pd.read_csv(fixture_path)
            st.info(f"Loaded synthetic fixture: {len(df_to_analyze)} rows")

    if df_to_analyze is not None:
        st.markdown("---")
        st.markdown("### Execution Pipeline Results")

        cfg = ExperimentConfig(
            minimum_meaningful_effect_absolute=d_min_custom,
            alpha=alpha_custom,
            srm_alpha=srm_alpha_custom,
        )

        # 1. Validation
        clean_df, report = validate_dataframe(
            df_to_analyze,
            control_arm=cfg.control,
            treatment_arm=cfg.treatment,
        )

        if not report.is_valid or clean_df is None:
            st.error(f"❌ Data Validation Failed: {', '.join(report.blockers)}")
            if report.issues:
                st.write("**Issues encountered:**")
                st.json(report.issues)
        else:
            st.success(
                f"✅ Data Schema Validated: {report.retained_rows:,} rows retained under ITT protocol."
            )

            # 2. Integrity & SRM
            integ = check_integrity(report, cfg)
            c_srm1, c_srm2 = st.columns(2)
            with c_srm1:
                st.metric("Control Rows (Gate 30)", f"{integ.n_control:,}")
            with c_srm2:
                st.metric("Treatment Rows (Gate 40)", f"{integ.n_treatment:,}")

            if integ.srm_status == "pass":
                st.success(
                    f"✅ SRM Test PASSED (p = {integ.srm_pvalue:.6f} >= {integ.srm_threshold})"
                )
            else:
                st.error(f"❌ SRM Test FAILED (p = {integ.srm_pvalue:.6f} < {integ.srm_threshold})")

            # 3. Primary Effect
            eff = calculate_retention_effect(clean_df, cfg)
            dec = evaluate_decision(integ, eff, d_min=d_min_custom, alpha=alpha_custom)

            st.markdown("#### Primary Decision & Effect")
            if dec.status == "supported":
                st.success(f"🎉 Status: SUPPORTED | Uplift: {eff.effect_percentage_points:+.2f} pp")
            elif dec.status == "not_supported":
                st.error(
                    f"⚠️ Status: NOT SUPPORTED | Effect: {eff.effect_percentage_points:+.2f} pp (Harm: {dec.is_harm_detected})"
                )
            else:
                st.warning(
                    f"⚖️ Status: INCONCLUSIVE | Effect: {eff.effect_percentage_points:+.2f} pp"
                )

            st.write(f"**Decision Explanation:** {dec.explanation}")

            # Export analysis bundle as downloadable JSON
            res_dict = {
                "quality": integ.to_dict(),
                "primary": eff.to_dict(),
                "decision": dec.to_dict(),
            }
            json_str = json.dumps(res_dict, indent=2)
            st.download_button(
                label="📥 Download Structured Analysis JSON",
                data=json_str,
                file_name="experiment_evaluation.json",
                mime="application/json",
            )
