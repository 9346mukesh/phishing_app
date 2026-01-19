#!/usr/bin/env python
"""Run Streamlit UI."""

import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "src/phishing/ui/app.py",
        ],
    )
