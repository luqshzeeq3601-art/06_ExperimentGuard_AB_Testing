"""Configuration schema, parsing, and validation for ExperimentGuard."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PlanningConfig:
    baseline_rate: float = 0.20
    target_power: float = 0.80
    mde_absolute: list[float] = field(default_factory=lambda: [0.0025, 0.005, 0.01])

    def __post_init__(self) -> None:
        if not (0.0 < self.baseline_rate < 1.0):
            raise ValueError(f"baseline_rate must be in (0, 1), got {self.baseline_rate}")
        if not (0.0 < self.target_power < 1.0):
            raise ValueError(f"target_power must be in (0, 1), got {self.target_power}")
        if not self.mde_absolute or any(mde <= 0 for mde in self.mde_absolute):
            raise ValueError("mde_absolute must be a non-empty list of positive floats")
        for mde in self.mde_absolute:
            if self.baseline_rate + mde >= 1.0:
                raise ValueError(
                    f"baseline_rate + mde must be < 1.0, got {self.baseline_rate} + {mde}"
                )


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_id: str = "cookie_cats_gate_placement"
    protocol_version: str = "1.0"
    control: str = "gate_30"
    treatment: str = "gate_40"
    primary_metric: str = "retention_7"
    alpha: float = 0.05
    alternative: str = "two-sided"
    confidence_method: str = "newcomb"
    minimum_meaningful_effect_absolute: float = 0.005
    expected_treatment_fraction: float = 0.5
    allocation_evidence: str = "assumed"
    srm_alpha: float = 0.001
    seed: int = 42
    bootstrap_replicates: int = 10000
    planning: PlanningConfig = field(default_factory=PlanningConfig)
    raw_yaml_sha256: str = ""

    def __post_init__(self) -> None:
        if not self.control or not self.treatment:
            raise ValueError("control and treatment variant names must be non-empty")
        if self.control == self.treatment:
            raise ValueError("control and treatment variants must be distinct")
        if not (0.0 < self.alpha < 1.0):
            raise ValueError(f"alpha must be in (0, 1), got {self.alpha}")
        if not (0.0 < self.srm_alpha < 1.0):
            raise ValueError(f"srm_alpha must be in (0, 1), got {self.srm_alpha}")
        if not (0.0 < self.expected_treatment_fraction < 1.0):
            raise ValueError(
                f"expected_treatment_fraction must be in (0, 1), got {self.expected_treatment_fraction}"
            )
        if self.minimum_meaningful_effect_absolute <= 0:
            raise ValueError("minimum_meaningful_effect_absolute must be positive")
        if self.alternative != "two-sided":
            raise ValueError(
                f"Only two-sided alternative is supported in v1, got {self.alternative}"
            )
        if self.confidence_method not in ("newcomb", "wilson", "normal"):
            raise ValueError(f"Unsupported confidence_method: {self.confidence_method}")
        if self.bootstrap_replicates < 100:
            raise ValueError("bootstrap_replicates must be at least 100")


def load_config(config_path: str | Path) -> ExperimentConfig:
    """Load and validate ExperimentConfig from a YAML file."""
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    raw_bytes = path.read_bytes()
    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()

    data: dict[str, Any] = yaml.safe_load(raw_bytes.decode("utf-8")) or {}
    planning_data = data.pop("planning", {})
    planning_cfg = PlanningConfig(**planning_data) if planning_data else PlanningConfig()

    return ExperimentConfig(
        planning=planning_cfg,
        raw_yaml_sha256=sha256_hash,
        **data,
    )
