"""Streamlit Cloud entrypoint for the NOHS Super Dashboard v_dc_8 release."""

import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).with_name("super_dashboard_production_v _dc_8_09_2026.py")),
    run_name="__main__",
)
