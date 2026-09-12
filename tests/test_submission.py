"""Smoke tests for submission assets — not the video itself."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"


def test_submission_docs_exist() -> None:
    assert (ROOT / "docs" / "SUBMISSION.md").is_file()
    assert (ROOT / "docs" / "VIDEO_SCRIPT.md").is_file()
    assert (ROOT / "LICENSE").is_file()


def test_video_assets_exist() -> None:
    for name in (
        "cover.svg",
        "cover.png",
        "rugpull-diff.html",
        "opening-card.svg",
        "pin-verify-quarantine.svg",
        "deployment-paths.svg",
    ):
        assert (ASSETS / name).is_file(), name
