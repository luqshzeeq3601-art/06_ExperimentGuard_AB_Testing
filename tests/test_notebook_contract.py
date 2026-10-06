"""Tests for verifying the notebook structure, cells, and reconciliation against package functions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from experimentguard.config import load_config
from experimentguard.data import load_and_validate_dataset
from experimentguard.effects import calculate_retention_effect
from experimentguard.integrity import check_integrity


def test_notebook_file_structure():
    nb_path = Path("notebooks/01_cookie_cats_analysis.ipynb")
    assert nb_path.is_file()

    nb_data = json.loads(nb_path.read_text(encoding="utf-8"))
    assert "cells" in nb_data
    assert len(nb_data["cells"]) >= 6

    # Verify key package imports exist in code cells
    code_sources = [
        "".join(c.get("source", [])) for c in nb_data["cells"] if c.get("cell_type") == "code"
    ]
    all_code = "\n".join(code_sources)
    assert "from experimentguard.config import load_config" in all_code
    assert "from experimentguard.data import load_and_validate_dataset" in all_code
    assert "from experimentguard.integrity import check_integrity" in all_code
    assert "from experimentguard.effects import" in all_code
    assert "from experimentguard.decision import evaluate_decision" in all_code


def test_reconcile_real_dataset_findings():
    data_path = Path("data/raw/cookie_cats.csv")
    cfg_path = Path("configs/experiment.yaml")

    if not data_path.is_file() or not cfg_path.is_file():
        pytest.skip("Real dataset or config not present")

    cfg = load_config(cfg_path)
    df, val = load_and_validate_dataset(data_path, cfg.control, cfg.treatment)
    assert val.is_valid is True

    integ = check_integrity(val, cfg, "data/source_manifest.json")
    assert integ.srm_status == "pass"

    res = calculate_retention_effect(df, cfg.primary_metric, cfg.control, cfg.treatment, cfg.alpha)
    assert res.n_control == 44700
    assert res.n_treatment == 45489
    assert res.retained_control == 8502
    assert res.retained_treatment == 8279

    # Rate gate_30 = 8502 / 44700 = 0.190201
    # Rate gate_40 = 8279 / 45489 = 0.182000
    assert res.rate_control == pytest.approx(0.1902013, abs=1e-5)
    assert res.rate_treatment == pytest.approx(0.1820000, abs=1e-5)
    assert res.effect_percentage_points == pytest.approx(-0.82013, abs=1e-3)
    assert res.pvalue < 0.005
