"""Measure full CLI wall time and sampled process RSS, separate from inner timings."""

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import psutil


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-rows", type=int, default=0)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    case = (
        f"benchmark-synthetic-{args.synthetic_rows}"
        if args.synthetic_rows
        else "benchmark-20261006"
    )
    output = root / "reports" / case
    output.mkdir(parents=True, exist_ok=True)
    data_path = "data/raw/cookie_cats.csv"
    if args.synthetic_rows:
        if args.synthetic_rows < 2:
            parser.error("--synthetic-rows must be at least 2")
        source = pd.read_csv(root / data_path)
        arms = [source[source["version"] == arm] for arm in ["gate_30", "gate_40"]]
        synthetic = pd.concat(
            [
                arm.sample(
                    n=args.synthetic_rows // 2 + (args.synthetic_rows % 2 if index else 0),
                    replace=True,
                    random_state=42 + index,
                )
                for index, arm in enumerate(arms)
            ],
            ignore_index=True,
        )
        synthetic["userid"] = range(1, args.synthetic_rows + 1)
        synthetic.to_csv(output / "input.csv", index=False)
        data_path = f"reports/{case}/input.csv"
    command = [
        sys.executable,
        "-m",
        "experimentguard",
        "analyze",
        "--data",
        data_path,
        "--config",
        "configs/experiment.yaml",
        "--out",
        str(output / "analysis"),
    ]
    if not args.synthetic_rows:
        command.extend(["--manifest", "data/source_manifest.json"])
    start = time.perf_counter()
    peak_rss = 0
    peak_process_count = 0
    with (output / "cli.log").open("w", encoding="utf-8") as log:
        child = subprocess.Popen(command, cwd=root, stdout=log, stderr=subprocess.STDOUT)
        process = psutil.Process(child.pid)
        while child.poll() is None:
            try:
                processes = [process, *process.children(recursive=True)]
                current_rss = 0
                for member in processes:
                    try:
                        current_rss += member.memory_info().rss
                    except psutil.NoSuchProcess:
                        continue
                peak_rss = max(peak_rss, current_rss)
                peak_process_count = max(peak_process_count, len(processes))
            except psutil.NoSuchProcess:
                break
            time.sleep(0.01)
        exit_code = child.wait()
    receipt = {
        "command": ["python", *command[1:]],
        "dataset_kind": "synthetic performance-only resample"
        if args.synthetic_rows
        else "public Cookie Cats benchmark",
        "synthetic_allocation": "Constructed balanced arms for capacity testing; no experimental inference"
        if args.synthetic_rows
        else None,
        "rows": args.synthetic_rows or 90189,
        "exit_code": exit_code,
        "measurement_scope": "Fresh Python CLI process: imports, CSV validation, analysis, figures, memo and export",
        "wall_seconds": round(time.perf_counter() - start, 4),
        "sampled_peak_rss_mib": round(peak_rss / 1024**2, 3),
        "rss_sample_interval_seconds": 0.01,
        "rss_scope": "Sum of launcher and recursive child-process RSS; shared pages may be counted more than once",
        "maximum_process_count": peak_process_count,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "psutil_version": psutil.__version__,
        "data_sha256": hashlib.sha256((root / data_path).read_bytes()).hexdigest(),
        "protocol_sha256": hashlib.sha256(
            (root / "configs/experiment.yaml").read_bytes()
        ).hexdigest(),
        "limitations": "RSS is sampled at 10ms and is distinct from tracemalloc Python allocations; no revenue or causal deployment claim.",
    }
    receipt["command"][receipt["command"].index("--out") + 1] = f"reports/{case}/analysis"
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
