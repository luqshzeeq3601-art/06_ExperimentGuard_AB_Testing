"""Tests for report rendering, figure generation, and analytical export bundle."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from experimentguard.config import ExperimentConfig
from experimentguard.data import load_and_validate_dataset
from experimentguard.integrity import check_integrity
from experimentguard.report import (
    export_full_report_bundle,
    generate_figures,
    render_decision_report,
    run_full_pipeline,
)


@pytest.fixture
def sample_report_result():
    csv_path = Path("tests/fixtures/valid_experiment.csv")
    cfg = ExperimentConfig(
        control="gate_30",
        treatment="gate_40",
        minimum_meaningful_effect_absolute=0.005,
    )
    df, val = load_and_validate_dataset(csv_path, cfg.control, cfg.treatment)
    integ = check_integrity(val, cfg)
    return run_full_pipeline(df, integ, cfg, val.data_sha256, run_id="test_report_run")


def test_render_decision_report_memo(sample_report_result):
    memo = render_decision_report(sample_report_result)
    assert "# ExperimentGuard: A/B Experiment Decision Memo" in memo
    assert "7-Day Retention (`retention_7`)" in memo
    assert "Data Integrity Status:" in memo
    assert "Prospective Sample Size Planning" in memo
    assert "Unresolved Limitations & Risk Disclosures" in memo


def test_generate_figures(sample_report_result):
    with tempfile.TemporaryDirectory() as tmp_dir:
        fig_dir = Path(tmp_dir) / "figures"
        paths = generate_figures(sample_report_result, fig_dir)
        assert len(paths) == 3
        for p in paths:
            f = Path(p)
            assert f.is_file()
            assert f.stat().st_size > 1000  # Non-empty PNG


def test_export_full_bundle(sample_report_result):
    cfg_file = Path("configs/experiment.yaml")
    with tempfile.TemporaryDirectory() as tmp_dir:
        bundle = export_full_report_bundle(
            sample_report_result,
            out_dir=tmp_dir,
            config_path=cfg_file if cfg_file.is_file() else None,
            start_time=100.0,
        )
        assert len(bundle) > 0

        assert (Path(tmp_dir) / "quality.json").is_file()
        assert (Path(tmp_dir) / "analysis.json").is_file()
        assert (Path(tmp_dir) / "summary.csv").is_file()
        assert (Path(tmp_dir) / "power_plan.csv").is_file()
        assert (Path(tmp_dir) / "decision_report.md").is_file()
        assert (Path(tmp_dir) / "run_metadata.json").is_file()
        assert (Path(tmp_dir) / "figures" / "retention_rates.png").is_file()
        assert (Path(tmp_dir) / "figures" / "retention_effect.png").is_file()
        assert (Path(tmp_dir) / "figures" / "power_sensitivity.png").is_file()
