"""The demo must run from a clean state without manual reset."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_make_demo_exits_zero_and_shows_contrast() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "demo.scenario"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    output = result.stdout
    assert "WITHOUT CUSTOMS" in output
    assert "WITH CUSTOMS" in output
    assert "✓ Success" in output
    assert "withheld" in output
    assert "tools/call refused" in output
