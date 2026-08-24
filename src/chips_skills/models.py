from pathlib import Path
from typing import Literal

type Model = Literal["claude", "codex", "gemini"]


def discover_model(path: Path) -> Model | None:
    """
    Inspect directory structure to determine which model is being used.

    Return None if the model cannot be determined.
    """

    if (path / ".claude").exists() or (path / "CLAUDE.md").exists():
        return "claude"
    elif (path / ".codex").exists() or (path / "CODEX.md").exists():
        return "codex"
    elif (path / ".gemini").exists() or (path / "GEMINI.md").exists():
        return "gemini"
    else:
        return None
