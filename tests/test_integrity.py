"""Tests for configuration parsing, data validation, and integrity/SRM diagnostics."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from scipy.stats import binomtest

from experimentguard.config import ExperimentConfig, PlanningConfig, load_config
from experimentguard.data import (
    load_and_validate_dataset,
    parse_boolean_token,
    parse_integer_token,
)
from experimentguard.integrity import check_integrity


def test_boolean_token_parsing():
    assert parse_boolean_token("True") is True
    assert parse_boolean_token("true") is True
    assert parse_boolean_token("1") is True
    assert parse_boolean_token(1) is True
    assert parse_boolean_token(True) is True

    assert parse_boolean_token("False") is False
    assert parse_boolean_token("false") is False
    assert parse_boolean_token("0") is False
    assert parse_boolean_token(0) is False
    assert parse_boolean_token(False) is False

    with pytest.raises(ValueError, match="Invalid boolean token"):
        parse_boolean_token("yes")
    with pytest.raises(ValueError, match="Invalid boolean token"):
        parse_boolean_token("no")
    with pytest.raises(ValueError, match="Invalid boolean token"):
        parse_boolean_token("2")
    with pytest.raises(ValueError, match="Invalid boolean token"):
        parse_boolean_token("")


def test_integer_token_parsing():
    assert parse_integer_token("123", "userid") == 123
    assert parse_integer_token(456, "userid") == 456
    assert parse_integer_token(0, "sum_gamerounds") == 0
    assert parse_integer_token(7.0, "sum_gamerounds") == 7

    with pytest.raises(ValueError, match="non-integer float"):
        parse_integer_token(7.5, "sum_gamerounds")
    with pytest.raises(ValueError, match="non-integer string"):
        parse_integer_token("abc", "userid")
    with pytest.raises(ValueError, match="empty string"):
        parse_integer_token("", "userid")


def test_config_validation():
    cfg = ExperimentConfig()
    assert cfg.control == "gate_30"
    assert cfg.treatment == "gate_40"
    assert cfg.alpha == 0.05
    assert cfg.srm_alpha == 0.001

    with pytest.raises(ValueError, match="must be distinct"):
        ExperimentConfig(control="gate_30", treatment="gate_30")
    with pytest.raises(ValueError, match="alpha must be in"):
        ExperimentConfig(alpha=1.5)
    with pytest.raises(ValueError, match="srm_alpha must be in"):
        ExperimentConfig(srm_alpha=-0.01)
    with pytest.raises(ValueError, match="expected_treatment_fraction must be in"):
        ExperimentConfig(expected_treatment_fraction=1.0)
    with pytest.raises(ValueError, match="baseline_rate must be in"):
        PlanningConfig(baseline_rate=1.2)


def test_load_config_file():
    cfg_file = Path("configs/experiment.yaml")
    if cfg_file.is_file():
        cfg = load_config(cfg_file)
        assert cfg.control == "gate_30"
        assert cfg.treatment == "gate_40"
        assert len(cfg.raw_yaml_sha256) == 64


def test_dataset_validation_success():
    csv_content = """userid,version,sum_gamerounds,retention_1,retention_7
1,gate_30,10,True,False
2,gate_30,0,False,False
3,gate_40,25,True,True
4,gate_40,5,False,True
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        tmp_path = f.name

    try:
        df, report = load_and_validate_dataset(tmp_path, "gate_30", "gate_40")
        assert df is not None
        assert report.is_valid is True
        assert report.input_rows == 4
        assert report.retained_rows == 4
        assert report.unique_users == 4
        assert report.zero_rounds_count == 1
        assert report.arm_counts == {"gate_30": 2, "gate_40": 2}
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_dataset_validation_failures():
    # 1. Duplicate user ID
    csv_dup = """userid,version,sum_gamerounds,retention_1,retention_7
1,gate_30,10,True,False
1,gate_40,20,True,False
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_dup)
        tmp_dup = f.name
    try:
        df, report = load_and_validate_dataset(tmp_dup, "gate_30", "gate_40")
        assert df is None
        assert report.is_valid is False
        assert report.duplicate_user_ids == 1
        assert any("Duplicate user IDs" in b for b in report.blockers)
    finally:
        Path(tmp_dup).unlink(missing_ok=True)

    # 2. Missing column
    csv_missing = """userid,version,sum_gamerounds,retention_1
1,gate_30,10,True
2,gate_40,20,True
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_missing)
        tmp_missing = f.name
    try:
        df, report = load_and_validate_dataset(tmp_missing, "gate_30", "gate_40")
        assert df is None
        assert report.is_valid is False
        assert any("Missing required columns" in b for b in report.blockers)
    finally:
        Path(tmp_missing).unlink(missing_ok=True)


def test_srm_diagnostic():
    cfg = ExperimentConfig(srm_alpha=0.001, expected_treatment_fraction=0.5)

    # Balanced case (500 vs 500)
    csv_bal = "\n".join(
        ["userid,version,sum_gamerounds,retention_1,retention_7"]
        + [f"{i},gate_30,5,True,False" for i in range(1, 501)]
        + [f"{i},gate_40,5,True,False" for i in range(501, 1001)]
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_bal)
        tmp_bal = f.name
    try:
        df, rep = load_and_validate_dataset(tmp_bal)
        assert rep.is_valid is True
        integ = check_integrity(rep, cfg)
        assert integ.srm_status == "pass"
        assert integ.srm_pvalue == pytest.approx(1.0)
    finally:
        Path(tmp_bal).unlink(missing_ok=True)

    # Severe SRM failure (400 vs 600 in N=1000)
    csv_srm = "\n".join(
        ["userid,version,sum_gamerounds,retention_1,retention_7"]
        + [f"{i},gate_30,5,True,False" for i in range(1, 401)]
        + [f"{i},gate_40,5,True,False" for i in range(401, 1001)]
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_srm)
        tmp_srm = f.name
    try:
        df, rep = load_and_validate_dataset(tmp_srm)
        assert rep.is_valid is True
        integ = check_integrity(rep, cfg)
        expected_p = binomtest(600, 1000, 0.5, alternative="two-sided").pvalue
        assert integ.srm_status == "fail"
        assert integ.srm_pvalue == pytest.approx(expected_p)
        assert integ.status == "fail"
        assert any("Sample Ratio Mismatch detected" in b for b in integ.blockers)
    finally:
        Path(tmp_srm).unlink(missing_ok=True)
