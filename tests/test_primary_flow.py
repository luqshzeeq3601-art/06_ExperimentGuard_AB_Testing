"""Tests for primary end-to-end flow: validate -> integrity -> effect -> decision -> export."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from experimentguard.config import ExperimentConfig
from experimentguard.data import load_and_validate_dataset
from experimentguard.integrity import check_integrity
from experimentguard.report import export_primary_outputs, run_primary_pipeline


def test_primary_flow_valid_fixture():
    valid_csv = Path("tests/fixtures/valid_experiment.csv")
    assert valid_csv.is_file()

    cfg = ExperimentConfig(
        control="gate_30",
        treatment="gate_40",
        minimum_meaningful_effect_absolute=0.005,
        alpha=0.05,
    )

    df, val_rep = load_and_validate_dataset(valid_csv, cfg.control, cfg.treatment)
    assert val_rep.is_valid is True
    assert df is not None
    assert len(df) == 10

    integ = check_integrity(val_rep, cfg)
    assert integ.status == "provisional"

    result = run_primary_pipeline(df, integ, cfg, val_rep.data_sha256, run_id="test_run_01")
    assert result.primary is not None
    assert result.primary.n_control == 5
    assert result.primary.n_treatment == 5
    assert result.primary.retained_control == 2  # rows 103, 105
    assert result.primary.retained_treatment == 1  # row 205
    assert result.primary.rate_control == pytest.approx(0.40)
    assert result.primary.rate_treatment == pytest.approx(0.20)
    assert result.primary.effect_absolute == pytest.approx(-0.20)

    # Test export
    with tempfile.TemporaryDirectory() as tmp_dir:
        export_primary_outputs(result, tmp_dir)
        p_analysis = Path(tmp_dir) / "analysis.json"
        p_quality = Path(tmp_dir) / "quality.json"
        p_summary = Path(tmp_dir) / "summary.csv"

        assert p_analysis.is_file()
        assert p_quality.is_file()
        assert p_summary.is_file()

        data_json = json.loads(p_analysis.read_text(encoding="utf-8"))
        assert data_json["experiment_id"] == "cookie_cats_gate_placement"
        assert data_json["primary"]["retained_control"] == 2
        assert data_json["primary"]["retained_treatment"] == 1


def test_primary_flow_invalid_fixture():
    invalid_csv = Path("tests/fixtures/invalid_experiment.csv")
    assert invalid_csv.is_file()

    cfg = ExperimentConfig(control="gate_30", treatment="gate_40")
    df, val_rep = load_and_validate_dataset(invalid_csv, cfg.control, cfg.treatment)
    assert val_rep.is_valid is False
    assert df is None

    integ = check_integrity(val_rep, cfg)
    assert integ.status == "fail"

    result = run_primary_pipeline(df, integ, cfg, val_rep.data_sha256, run_id="test_run_invalid")
    assert result.primary is None
    assert result.decision.status == "blocked"

    with tempfile.TemporaryDirectory() as tmp_dir:
        export_primary_outputs(result, tmp_dir)
        p_analysis = Path(tmp_dir) / "analysis.json"
        p_quality = Path(tmp_dir) / "quality.json"
        assert p_analysis.is_file()
        assert p_quality.is_file()

        data_json = json.loads(p_analysis.read_text(encoding="utf-8"))
        assert data_json["quality"]["status"] == "fail"
        assert data_json["decision"]["status"] == "blocked"
        assert data_json["primary"] is None
