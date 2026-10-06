"""Root entrypoint for Streamlit dashboard (compatible with Streamlit Cloud & HF Spaces)."""

import runpy
from pathlib import Path

app_path = Path(__file__).resolve().parent / "app" / "streamlit_app.py"
runpy.run_path(str(app_path), run_name="__main__")
