"""Tests for ExperimentGuard CLI subcommands: validate, analyze, and plan."""

from __future__ import annotations

import tempfile
from pathlib import Path

from experimentguard.cli import main


def test_cli_validate_success():
    valid_csv = Path("tests/fixtures/valid_experiment.csv")
    cfg_yaml = Path("configs/experiment.yaml")

    with tempfile.TemporaryDirectory() as tmp_dir:
        exit_code = main(
            [
                "validate",
                "--data",
                str(valid_csv),
                "--config",
                str(cfg_yaml),
                "--out",
                tmp_dir,
            ]
        )
        assert exit_code == 0
        assert (Path(tmp_dir) / "quality.json").is_file()
        assert (Path(tmp_dir) / "run_metadata.json").is_file()


def test_cli_validate_failure():
    invalid_csv = Path("tests/fixtures/invalid_experiment.csv")
    cfg_yaml = Path("configs/experiment.yaml")

    with tempfile.TemporaryDirectory() as tmp_dir:
        exit_code = main(
            [
                "validate",
                "--data",
                str(invalid_csv),
                "--config",
                str(cfg_yaml),
                "--out",
                tmp_dir,
            ]
        )
        assert exit_code == 2
        assert (Path(tmp_dir) / "quality.json").is_file()


def test_cli_analyze_success():
    valid_csv = Path("tests/fixtures/valid_experiment.csv")
    cfg_yaml = Path("configs/experiment.yaml")

    with tempfile.TemporaryDirectory() as tmp_dir:
        exit_code = main(
            [
                "analyze",
                "--data",
                str(valid_csv),
                "--config",
                str(cfg_yaml),
                "--out",
                tmp_dir,
            ]
        )
        assert exit_code == 0
        assert (Path(tmp_dir) / "analysis.json").is_file()
        assert (Path(tmp_dir) / "decision_report.md").is_file()
        assert (Path(tmp_dir) / "figures" / "retention_rates.png").is_file()


def test_cli_analyze_blocked():
    invalid_csv = Path("tests/fixtures/invalid_experiment.csv")
    cfg_yaml = Path("configs/experiment.yaml")

    with tempfile.TemporaryDirectory() as tmp_dir:
        exit_code = main(
            [
                "analyze",
                "--data",
                str(invalid_csv),
                "--config",
                str(cfg_yaml),
                "--out",
                tmp_dir,
            ]
        )
        assert exit_code == 2
        assert (Path(tmp_dir) / "analysis.json").is_file()


def test_cli_plan():
    cfg_yaml = Path("configs/experiment.yaml")

    with tempfile.TemporaryDirectory() as tmp_dir:
        exit_code = main(
            [
                "plan",
                "--config",
                str(cfg_yaml),
                "--out",
                tmp_dir,
            ]
        )
        assert exit_code == 0
        assert (Path(tmp_dir) / "power_plan.csv").is_file()
        assert (Path(tmp_dir) / "figures" / "power_sensitivity.png").is_file()
        assert (Path(tmp_dir) / "run_metadata.json").is_file()
