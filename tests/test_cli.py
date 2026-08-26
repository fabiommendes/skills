from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from chips_skills import cli, local_repo

runner = CliRunner()


@pytest.fixture(autouse=True)
def fake_skills_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "skills-repo"
    monkeypatch.setattr(local_repo, "DEFAULT_SKILLS_ROOT", root)
    monkeypatch.setattr(cli, "DEFAULT_SKILLS_ROOT", root)
    return root


@pytest.fixture()
def project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    return project


def test_list_prints_bundled_skills() -> None:
    result = runner.invoke(cli.app, ["list"])

    assert result.exit_code == 0
    assert "python/python-functions" in result.output


def test_add_copies_skill_into_claude_dir(project_dir: Path) -> None:
    result = runner.invoke(cli.app, ["add", "python/python-functions", "--claude"])

    assert result.exit_code == 0
    installed = project_dir / ".claude" / "skills" / "python-functions" / "SKILL.md"
    assert installed.is_file()


def test_add_defaults_to_claude_when_no_flag_given(project_dir: Path) -> None:
    result = runner.invoke(cli.app, ["add", "python/python-functions"])

    assert result.exit_code == 0
    assert (project_dir / ".claude" / "skills" / "python-functions").is_dir()


def test_add_redirects_abbreviated_skill_name(project_dir: Path) -> None:
    result = runner.invoke(cli.app, ["add", "python/modules", "--claude"])

    assert result.exit_code == 0
    assert (project_dir / ".claude" / "skills" / "python-modules").is_dir()


def bundled_skill_names(category: str) -> set[str]:
    category_dir = local_repo.BUNDLED_SKILLS_ROOT / category
    return {p.name for p in category_dir.iterdir() if (p / "SKILL.md").is_file()}


def test_add_glob_installs_every_matching_skill(project_dir: Path) -> None:
    result = runner.invoke(cli.app, ["add", "python/*", "--claude"])

    assert result.exit_code == 0
    installed = {p.name for p in (project_dir / ".claude" / "skills").iterdir()}
    assert installed == bundled_skill_names("python")


def test_add_glob_no_match_fails(project_dir: Path) -> None:
    result = runner.invoke(cli.app, ["add", "nope/*", "--claude"])

    assert result.exit_code != 0


def test_add_glob_skips_already_installed_and_succeeds(project_dir: Path) -> None:
    first = runner.invoke(cli.app, ["add", "python/python-functions", "--claude"])
    second = runner.invoke(cli.app, ["add", "python/*", "--claude"])

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert "skip" in second.output
    installed = {p.name for p in (project_dir / ".claude" / "skills").iterdir()}
    assert installed == bundled_skill_names("python")


def test_add_unknown_skill_fails(project_dir: Path) -> None:
    result = runner.invoke(cli.app, ["add", "python/does-not-exist"])

    assert result.exit_code != 0


def test_add_twice_fails_on_second_install(project_dir: Path) -> None:
    first = runner.invoke(cli.app, ["add", "python/python-functions", "--claude"])
    second = runner.invoke(cli.app, ["add", "python/python-functions", "--claude"])

    assert first.exit_code == 0
    assert second.exit_code != 0


def test_add_force_overwrites_existing_skill(project_dir: Path) -> None:
    installed = project_dir / ".claude" / "skills" / "python-functions"
    first = runner.invoke(cli.app, ["add", "python/python-functions", "--claude"])
    stale_marker = installed / "stale.txt"
    stale_marker.write_text("stale")

    second = runner.invoke(
        cli.app, ["add", "python/python-functions", "--claude", "--force"]
    )

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert installed.is_dir()
    assert not stale_marker.exists()


def test_add_force_overwrites_in_glob_mode(project_dir: Path) -> None:
    first = runner.invoke(cli.app, ["add", "python/*", "--claude"])
    second = runner.invoke(cli.app, ["add", "python/*", "--claude", "--force"])

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert "skip" not in second.output
    installed = {p.name for p in (project_dir / ".claude" / "skills").iterdir()}
    assert installed == bundled_skill_names("python")


def test_new_creates_skill_and_opens_editor(monkeypatch: pytest.MonkeyPatch) -> None:
    run_mock = MagicMock()
    monkeypatch.setattr(cli.subprocess, "run", run_mock)
    monkeypatch.setenv("EDITOR", "my-editor")

    result = runner.invoke(cli.app, ["new", "generic/my-new-skill"])

    assert result.exit_code == 0
    run_mock.assert_called_once()
    assert run_mock.call_args.args[0][0] == "my-editor"

    repo = local_repo.SkillRepo(root=cli.DEFAULT_SKILLS_ROOT)
    skill = repo.get_skill("generic/my-new-skill").load_skill("my-new-skill")
    assert skill.name == "my-new-skill"


def test_new_duplicate_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.subprocess, "run", MagicMock())

    first = runner.invoke(cli.app, ["new", "generic/dup"])
    second = runner.invoke(cli.app, ["new", "generic/dup"])

    assert first.exit_code == 0
    assert second.exit_code != 0


def test_edit_opens_editor_for_existing_skill(monkeypatch: pytest.MonkeyPatch) -> None:
    run_mock = MagicMock()
    monkeypatch.setattr(cli.subprocess, "run", run_mock)
    monkeypatch.setenv("EDITOR", "my-editor")

    result = runner.invoke(cli.app, ["edit", "python/python-functions"])

    assert result.exit_code == 0
    run_mock.assert_called_once()
    args = run_mock.call_args.args[0]
    assert args[0] == "my-editor"
    assert args[1].endswith("python-functions/SKILL.md")


def test_edit_redirects_abbreviated_skill_name(monkeypatch: pytest.MonkeyPatch) -> None:
    run_mock = MagicMock()
    monkeypatch.setattr(cli.subprocess, "run", run_mock)

    result = runner.invoke(cli.app, ["edit", "python/modules"])

    assert result.exit_code == 0
    args = run_mock.call_args.args[0]
    assert args[1].endswith("python-modules/SKILL.md")


def test_edit_unknown_skill_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.subprocess, "run", MagicMock())

    result = runner.invoke(cli.app, ["edit", "python/does-not-exist"])

    assert result.exit_code != 0


def test_update_syncs_stale_skill_with_repo(project_dir: Path) -> None:
    runner.invoke(cli.app, ["add", "python/python-functions", "--claude"])
    installed = project_dir / ".claude" / "skills" / "python-functions"
    stale_marker = installed / "stale.txt"
    stale_marker.write_text("stale")

    result = runner.invoke(cli.app, ["update"])

    assert result.exit_code == 0
    assert "updated" in result.output
    assert not stale_marker.exists()


def test_update_reports_up_to_date_skill(project_dir: Path) -> None:
    runner.invoke(cli.app, ["add", "python/python-functions", "--claude"])

    result = runner.invoke(cli.app, ["update"])

    assert result.exit_code == 0
    assert "up to date" in result.output


def test_update_with_no_skills_installed_reports_none(project_dir: Path) -> None:
    result = runner.invoke(cli.app, ["update"])

    assert result.exit_code == 0
    assert "No skills installed." in result.output


def test_update_skips_skill_not_found_in_repo(project_dir: Path) -> None:
    runner.invoke(cli.app, ["add", "python/python-functions", "--claude"])
    installed_root = project_dir / ".claude" / "skills"
    orphan = installed_root / "orphan-skill"
    orphan.mkdir()
    (orphan / "SKILL.md").write_text(
        "---\nname: orphan-skill\ndescription: d\n---\n\nBody.\n"
    )

    result = runner.invoke(cli.app, ["update"])

    assert result.exit_code == 0
    assert "not found in repo" in result.output
    assert orphan.is_dir()


def test_update_respects_model_flag(project_dir: Path) -> None:
    runner.invoke(cli.app, ["add", "python/python-functions", "--claude"])
    runner.invoke(cli.app, ["add", "python/python-functions", "--codex"])
    claude_dir = project_dir / ".claude" / "skills" / "python-functions"
    codex_dir = project_dir / ".codex" / "skills" / "python-functions"
    claude_marker = claude_dir / "stale.txt"
    codex_marker = codex_dir / "stale.txt"
    claude_marker.write_text("stale")
    codex_marker.write_text("stale")

    result = runner.invoke(cli.app, ["update", "--claude"])

    assert result.exit_code == 0
    assert not claude_marker.exists()
    assert codex_marker.exists()


def test_get_model_prefers_explicit_flag() -> None:
    assert cli._get_model(claude=False, codex=True, gemini=False) == "codex"


def test_get_model_defaults_to_claude() -> None:
    assert cli._get_model(claude=False, codex=False, gemini=False) == "claude"
