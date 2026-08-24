from __future__ import annotations

from pathlib import Path

from chips_skills.models import discover_model


def test_discover_model_detects_claude(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").touch()
    assert discover_model(tmp_path) == "claude"


def test_discover_model_detects_codex(tmp_path: Path) -> None:
    (tmp_path / ".codex").mkdir()
    assert discover_model(tmp_path) == "codex"


def test_discover_model_detects_gemini(tmp_path: Path) -> None:
    (tmp_path / "GEMINI.md").touch()
    assert discover_model(tmp_path) == "gemini"


def test_discover_model_returns_none_when_unknown(tmp_path: Path) -> None:
    assert discover_model(tmp_path) is None
