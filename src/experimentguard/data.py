"""Data ingestion, strict schema parsing, and quality validation for ExperimentGuard."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class ValidationReport:
    is_valid: bool
    input_rows: int
    retained_rows: int
    columns: list[str]
    unique_users: int
    arm_counts: dict[str, int]
    zero_rounds_count: int
    missing_values: dict[str, int]
    duplicate_user_ids: int
    issues: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    data_sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "input_rows": self.input_rows,
            "retained_rows": self.retained_rows,
            "columns": self.columns,
            "unique_users": self.unique_users,
            "arm_counts": self.arm_counts,
            "zero_rounds_count": self.zero_rounds_count,
            "missing_values": self.missing_values,
            "duplicate_user_ids": self.duplicate_user_ids,
            "issues": self.issues,
            "blockers": self.blockers,
            "data_sha256": self.data_sha256,
        }


REQUIRED_COLUMNS = [
    "userid",
    "version",
    "sum_gamerounds",
    "retention_1",
    "retention_7",
]

TRUE_TOKENS = {"true", "1"}
FALSE_TOKENS = {"false", "0"}


def parse_boolean_token(val: Any) -> bool:
    """Strictly parse a boolean token. Rejects ambiguous/truthy string traps."""
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        if val == 1:
            return True
        if val == 0:
            return False
        raise ValueError(f"Invalid numeric boolean value: {val}")
    if isinstance(val, str):
        cleaned = val.strip().lower()
        if cleaned in TRUE_TOKENS:
            return True
        if cleaned in FALSE_TOKENS:
            return False
        raise ValueError(f"Invalid boolean token: '{val}'")
    raise ValueError(f"Cannot parse boolean from type {type(val).__name__}: {val}")


def parse_integer_token(val: Any, col_name: str) -> int:
    """Strictly parse integer. Rejects floats, non-integers, and NaN."""
    if isinstance(val, (int,)):
        return val
    if isinstance(val, float):
        if val.is_integer():
            return int(val)
        raise ValueError(f"Column '{col_name}' contains non-integer float: {val}")
    if isinstance(val, str):
        cleaned = val.strip()
        if not cleaned:
            raise ValueError(f"Column '{col_name}' contains empty string")
        try:
            return int(cleaned)
        except ValueError:
            raise ValueError(f"Column '{col_name}' contains non-integer string: '{val}'")
    raise ValueError(f"Cannot parse integer for '{col_name}' from type {type(val).__name__}")


def load_and_validate_dataset(
    data_path: str | Path,
    control_arm: str = "gate_30",
    treatment_arm: str = "gate_40",
) -> tuple[pd.DataFrame | None, ValidationReport]:
    """Ingest CSV, validate all quality requirements, and return typed DataFrame and Report.

    Does NOT silently remove zero-round users or non-returners.
    Rejects duplicate user IDs, invalid tokens, empty arms, or missing required fields.
    """
    path = Path(data_path)
    if not path.is_file():
        report = ValidationReport(
            is_valid=False,
            input_rows=0,
            retained_rows=0,
            columns=[],
            unique_users=0,
            arm_counts={},
            zero_rounds_count=0,
            missing_values={},
            duplicate_user_ids=0,
            issues=[f"File not found: {path}"],
            blockers=[f"File not found: {path}"],
        )
        return None, report

    raw_bytes = path.read_bytes()
    data_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    issues: list[str] = []
    blockers: list[str] = []

    try:
        content_str = raw_bytes.decode("utf-8-sig")
    except Exception as e:
        report = ValidationReport(
            is_valid=False,
            input_rows=0,
            retained_rows=0,
            columns=[],
            unique_users=0,
            arm_counts={},
            zero_rounds_count=0,
            missing_values={},
            duplicate_user_ids=0,
            issues=[f"Failed to decode CSV as UTF-8: {e}"],
            blockers=["CSV encoding error"],
            data_sha256=data_sha256,
        )
        return None, report

    reader = csv.reader(content_str.splitlines())
    try:
        header = next(reader)
    except StopIteration:
        report = ValidationReport(
            is_valid=False,
            input_rows=0,
            retained_rows=0,
            columns=[],
            unique_users=0,
            arm_counts={},
            zero_rounds_count=0,
            missing_values={},
            duplicate_user_ids=0,
            issues=["CSV file is empty"],
            blockers=["Empty dataset"],
            data_sha256=data_sha256,
        )
        return None, report

    cleaned_header = [c.strip() for c in header]
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in cleaned_header]
    if missing_cols:
        report = ValidationReport(
            is_valid=False,
            input_rows=0,
            retained_rows=0,
            columns=cleaned_header,
            unique_users=0,
            arm_counts={},
            zero_rounds_count=0,
            missing_values={},
            duplicate_user_ids=0,
            issues=[f"Missing required columns: {missing_cols}"],
            blockers=[f"Missing required columns: {missing_cols}"],
            data_sha256=data_sha256,
        )
        return None, report

    col_idx = {c: cleaned_header.index(c) for c in REQUIRED_COLUMNS}

    parsed_uids: list[int] = []
    parsed_versions: list[str] = []
    parsed_rounds: list[int] = []
    parsed_r1: list[bool] = []
    parsed_r7: list[bool] = []

    seen_uids: set[int] = set()
    dup_uids = 0
    zero_rounds = 0
    arm_counts: dict[str, int] = {control_arm: 0, treatment_arm: 0}
    row_count = 0

    for line_num, row in enumerate(reader, start=2):
        if not row or all(not cell.strip() for cell in row):
            continue  # ignore blank trailing lines
        row_count += 1
        if len(row) < len(cleaned_header):
            issues.append(
                f"Line {line_num}: incomplete row ({len(row)} cols < {len(cleaned_header)})"
            )
            continue

        # userid
        raw_uid = row[col_idx["userid"]].strip()
        try:
            uid = parse_integer_token(raw_uid, "userid")
            if uid <= 0:
                issues.append(f"Line {line_num}: userid must be positive integer, got {uid}")
        except Exception as e:
            issues.append(f"Line {line_num}: {e}")
            continue

        if uid in seen_uids:
            dup_uids += 1
            issues.append(f"Line {line_num}: duplicate userid {uid}")
        seen_uids.add(uid)

        # version
        ver = row[col_idx["version"]].strip()
        if ver not in (control_arm, treatment_arm):
            issues.append(
                f"Line {line_num}: invalid version '{ver}' (expected '{control_arm}' or '{treatment_arm}')"
            )
        else:
            arm_counts[ver] = arm_counts.get(ver, 0) + 1

        # sum_gamerounds
        raw_rounds = row[col_idx["sum_gamerounds"]].strip()
        try:
            rounds = parse_integer_token(raw_rounds, "sum_gamerounds")
            if rounds < 0:
                issues.append(f"Line {line_num}: sum_gamerounds cannot be negative: {rounds}")
            elif rounds == 0:
                zero_rounds += 1
        except Exception as e:
            issues.append(f"Line {line_num}: {e}")
            continue

        # retention_1
        raw_r1 = row[col_idx["retention_1"]].strip()
        try:
            r1 = parse_boolean_token(raw_r1)
        except Exception as e:
            issues.append(f"Line {line_num}: retention_1 invalid: {e}")
            continue

        # retention_7
        raw_r7 = row[col_idx["retention_7"]].strip()
        try:
            r7 = parse_boolean_token(raw_r7)
        except Exception as e:
            issues.append(f"Line {line_num}: retention_7 invalid: {e}")
            continue

        parsed_uids.append(uid)
        parsed_versions.append(ver)
        parsed_rounds.append(rounds)
        parsed_r1.append(r1)
        parsed_r7.append(r7)

    if dup_uids > 0:
        blockers.append(f"Duplicate user IDs detected ({dup_uids} duplicates)")
    if arm_counts.get(control_arm, 0) == 0:
        blockers.append(f"Control arm '{control_arm}' has 0 rows")
    if arm_counts.get(treatment_arm, 0) == 0:
        blockers.append(f"Treatment arm '{treatment_arm}' has 0 rows")
    if row_count == 0:
        blockers.append("No data rows found in CSV")
    if issues:
        # If there were any structural row parsing failures
        if len(parsed_uids) != row_count or dup_uids > 0:
            blockers.append("Data validation errors encountered")

    is_valid = len(blockers) == 0

    report = ValidationReport(
        is_valid=is_valid,
        input_rows=row_count,
        retained_rows=len(parsed_uids) if is_valid else 0,
        columns=cleaned_header,
        unique_users=len(seen_uids),
        arm_counts=arm_counts,
        zero_rounds_count=zero_rounds,
        missing_values={},
        duplicate_user_ids=dup_uids,
        issues=issues[:20],  # cap display issues
        blockers=blockers,
        data_sha256=data_sha256,
    )

    if not is_valid:
        return None, report

    df = pd.DataFrame(
        {
            "userid": parsed_uids,
            "version": parsed_versions,
            "sum_gamerounds": parsed_rounds,
            "retention_1": parsed_r1,
            "retention_7": parsed_r7,
        }
    )
    return df, report


def validate_dataframe(
    df: pd.DataFrame,
    control_arm: str = "gate_30",
    treatment_arm: str = "gate_40",
) -> tuple[pd.DataFrame | None, ValidationReport]:
    """Validate an in-memory DataFrame using the strict ExperimentGuard ITT protocol."""
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8"
    ) as f:
        df.to_csv(f, index=False)
        tmp_path = Path(f.name)
    try:
        return load_and_validate_dataset(
            tmp_path, control_arm=control_arm, treatment_arm=treatment_arm
        )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
