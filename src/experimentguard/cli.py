"""Command-line interface for ExperimentGuard: validate, analyze, and plan."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from experimentguard.config import load_config
from experimentguard.data import load_and_validate_dataset
from experimentguard.integrity import check_integrity
from experimentguard.power import (
    plan_power_scenarios,
    power_scenarios_to_dataframe,
)
from experimentguard.report import (
    export_full_report_bundle,
    generate_figures,
    run_full_pipeline,
)


def cmd_validate(args: argparse.Namespace) -> int:
    """Execute validate command: schema validation and SRM integrity diagnostic."""
    start_t = time.time()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        cfg = load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return 2

    df, val_rep = load_and_validate_dataset(
        data_path=args.data,
        control_arm=cfg.control,
        treatment_arm=cfg.treatment,
    )

    integ = check_integrity(val_rep, cfg, manifest_path=args.manifest)

    # Export quality.json
    quality_path = out_dir / "quality.json"
    quality_path.write_text(json.dumps(integ.to_dict(), indent=2), encoding="utf-8")

    meta_path = out_dir / "run_metadata.json"
    meta = {
        "command": "validate",
        "data_path": str(args.data),
        "data_sha256": val_rep.data_sha256,
        "config_path": str(args.config),
        "config_sha256": cfg.raw_yaml_sha256,
        "runtime_seconds": round(time.time() - start_t, 4),
        "quality_status": integ.status,
        "srm_status": integ.srm_status,
        "blockers": integ.blockers,
        "limitations": integ.limitations,
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Validation completed. Status: {integ.status.upper()}")
    print(f"  Rows: {val_rep.input_rows:,} total, {val_rep.retained_rows:,} retained")
    print(f"  SRM test: {integ.srm_status.upper()} (p={integ.srm_pvalue:.6f})")
    print(f"  Output saved to: {out_dir}")

    if integ.status == "fail":
        print(f"Validation failed with blockers: {integ.blockers}", file=sys.stderr)
        return 2

    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Execute analyze command: full validation, primary/secondary effect estimation, figures, and memo."""
    start_t = time.time()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        cfg = load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return 2

    df, val_rep = load_and_validate_dataset(
        data_path=args.data,
        control_arm=cfg.control,
        treatment_arm=cfg.treatment,
    )

    integ = check_integrity(val_rep, cfg, manifest_path=args.manifest)

    result = run_full_pipeline(
        df=df,
        integrity=integ,
        config=cfg,
        data_sha256=val_rep.data_sha256,
        run_id=out_dir.name,
        include_secondary=True,
    )

    export_full_report_bundle(
        result=result,
        out_dir=out_dir,
        config_path=args.config,
        manifest_path=args.manifest,
        start_time=start_t,
    )

    print(f"Analysis completed. Decision: {result.decision.status.upper()}")
    if result.primary is not None:
        p = result.primary
        print(f"  Primary metric: {p.metric}")
        print(f"  Control rate ({p.control}): {p.rate_control * 100:.2f}% (N={p.n_control:,})")
        print(
            f"  Treatment rate ({p.treatment}): {p.rate_treatment * 100:.2f}% (N={p.n_treatment:,})"
        )
        print(
            f"  Effect (B - A): {p.effect_percentage_points:+.2f} pp (95% CI: [{p.ci_absolute[0] * 100:+.2f}, {p.ci_absolute[1] * 100:+.2f}])"
        )
        print(f"  p-value: {p.pvalue:.4e} ({p.test_method})")
    print(f"  Decision explanation: {result.decision.explanation}")
    print(f"  Reports & figures exported to: {out_dir}")

    if result.decision.status == "blocked":
        return 2

    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    """Execute plan command: prospective power planning without observed data."""
    start_t = time.time()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        cfg = load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return 2

    scenarios = plan_power_scenarios(
        baseline_rate=cfg.planning.baseline_rate,
        mde_list=cfg.planning.mde_absolute,
        alpha=cfg.alpha,
        target_power=cfg.planning.target_power,
        expected_treatment_fraction=cfg.expected_treatment_fraction,
    )

    df_plan = power_scenarios_to_dataframe(scenarios)
    plan_csv = out_dir / "power_plan.csv"
    df_plan.to_csv(plan_csv, index=False, encoding="utf-8")

    # Generate power sensitivity figure
    from experimentguard.report import FullAnalysisResult

    mock_integ = check_integrity(
        type("VR", (), {"is_valid": False, "arm_counts": {}, "blockers": [], "limitations": []})(),
        cfg,
    )
    mock_result = FullAnalysisResult(
        schema_version="1.0",
        experiment_id=cfg.experiment_id,
        run_id="power_planning",
        created_at_utc="",
        data_sha256="",
        protocol_sha256=cfg.raw_yaml_sha256,
        package_versions={},
        seed=cfg.seed,
        quality=mock_integ,
        primary=None,
        decision=type(
            "DR",
            (),
            {"status": "planning", "practical_threshold_absolute": 0.005, "to_dict": lambda s: {}},
        )(),
        power_planning=scenarios,
    )
    generate_figures(mock_result, out_dir / "figures")

    meta_path = out_dir / "run_metadata.json"
    meta = {
        "command": "plan",
        "config_path": str(args.config),
        "config_sha256": cfg.raw_yaml_sha256,
        "runtime_seconds": round(time.time() - start_t, 4),
        "scenarios": [s.to_dict() for s in scenarios],
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print("Prospective sample size planning completed.")
    print(f"  Baseline rate: {cfg.planning.baseline_rate * 100:.1f}%")
    print(f"  Target power: {cfg.planning.target_power * 100:.0f}% (alpha={cfg.alpha})")
    for sc in scenarios:
        print(
            f"  - MDE {sc.mde_percentage_points:.2f} pp -> Total N = {sc.required_n_total:,} ({sc.required_n_control:,} per arm)"
        )
    print(f"  Output saved to: {out_dir}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="experimentguard",
        description="ExperimentGuard: Trustworthy retention A/B experiment analysis & planning.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate
    p_val = subparsers.add_parser("validate", help="Validate experiment CSV schema and SRM.")
    p_val.add_argument("--data", required=True, help="Path to raw experiment CSV.")
    p_val.add_argument("--manifest", required=False, help="Path to source manifest JSON.")
    p_val.add_argument("--config", required=True, help="Path to experiment.yaml configuration.")
    p_val.add_argument("--out", required=True, help="Output directory for validation artifacts.")

    # analyze
    p_ana = subparsers.add_parser(
        "analyze", help="Run full A/B analysis, decision rules, figures, and report."
    )
    p_ana.add_argument("--data", required=True, help="Path to raw experiment CSV.")
    p_ana.add_argument("--manifest", required=False, help="Path to source manifest JSON.")
    p_ana.add_argument("--config", required=True, help="Path to experiment.yaml configuration.")
    p_ana.add_argument(
        "--out", required=True, help="Output directory for analytical report bundle."
    )

    # plan
    p_pla = subparsers.add_parser(
        "plan", help="Calculate prospective power and sample size requirements."
    )
    p_pla.add_argument("--config", required=True, help="Path to experiment.yaml configuration.")
    p_pla.add_argument("--out", required=True, help="Output directory for power plan artifacts.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return cmd_validate(args)
    elif args.command == "analyze":
        return cmd_analyze(args)
    elif args.command == "plan":
        return cmd_plan(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
