# 06. Technology Stack and Commands

## 1. Stack

| Layer | Tool | Reason |
|---|---|---|
| Runtime/environment | Python 3.11 preferred, local venv/pip | CPU-only Windows portability |
| Data | pandas, NumPy | Typed CSV and seeded calculations |
| Statistics | SciPy, statsmodels | SRM, binary tests/intervals, power |
| Configuration | PyYAML, typed standard-library objects | Explicit settings |
| Reports | matplotlib, JSON/CSV/Markdown | Portable evidence |
| Notebook | Jupyter, nbconvert, ipykernel | Fresh-kernel verification |
| Checks | pytest, ruff | Correctness and lint |
| CI | GitHub Actions | Synthetic-fixture tests without credentials |

At T01 verify interpreter availability and resolve a compatible dependency set into `requirements.lock.txt`. Record actual versions. No exact package pins are fabricated here. Match official API documentation to installed versions.

## 2. Command status

**Commands are planned interfaces. Code and environment do not exist yet.** Establish and verify them during execution. Run PowerShell in this project folder using explicit venv Python to avoid activation-policy issues.

## 3. Setup at T01

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -c "import experimentguard, scipy, statsmodels; print('imports passed')"
```

Initial lock creation resolves `requirements.in`, freezes the successful environment, then proves fresh installation from lock. If `py -3.11` is missing, inspect available interpreters and choose a compatible one first. The eventual project must not require a Codex-only bundled interpreter.

## 4. Data and quality

```powershell
Get-FileHash -LiteralPath .\data\raw\cookie_cats.csv -Algorithm SHA256
.\.venv\Scripts\python.exe -m experimentguard validate --data data/raw/cookie_cats.csv --manifest data/source_manifest.json --config configs/experiment.yaml --out reports/quality-check
```

Acquire data through verified source workflow. Do not guess a download URL.

## 5. Analysis and planning

```powershell
.\.venv\Scripts\python.exe -m experimentguard analyze --data data/raw/cookie_cats.csv --manifest data/source_manifest.json --config configs/experiment.yaml --out reports/cookie-cats-v1
.\.venv\Scripts\python.exe -m experimentguard plan --config configs/experiment.yaml --out reports/power-v1
```

Analyze produces integrity, primary effect, decision, power table, report, figures, metadata. Plan works without observed data and labels inputs as assumptions. Use fresh output directories; never weaken a quality rule to obtain exit 0.

## 6. Verification and notebook

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider --basetemp .pytest_tmp
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m ruff format --check src tests
.\.venv\Scripts\python.exe -m ipykernel install --prefix .venv --name experimentguard --display-name ExperimentGuard
.\.venv\Scripts\python.exe -m nbconvert --to notebook --execute notebooks/01_cookie_cats_analysis.ipynb --ExecutePreprocessor.kernel_name=experimentguard --ExecutePreprocessor.timeout=300 --output executed_cookie_cats --output-dir reports/notebook
```

Create output directory and confirm kernel points to project venv. Notebook paths resolve from project root independent of initial kernel working directory.

## 7. CI

- Install lock and editable package.
- Run lint, tests, synthetic end-to-end report.
- No live download or Kaggle credentials required.
- Real-data CLI/notebook remain local release checks with source hash recorded.
- Hosted CI is unverified until a workflow actually runs after a separately requested push.
