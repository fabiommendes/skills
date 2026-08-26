import os
import shutil
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.padding import Padding

from .console import stderr, stdout
from .local_repo import DEFAULT_SKILLS_ROOT, Skill, SkillRepo
from .models import Model

__all__ = ["main", "add", "edit", "new", "list_", "update"]

app = typer.Typer()

CLAUDE_OPT = Annotated[bool, typer.Option("--claude", help="Force using Claude model.")]
CODEX_OPT = Annotated[bool, typer.Option("--codex", help="Force using Codex model.")]
GEMINI_OPT = Annotated[bool, typer.Option("--gemini", help="Force using Gemini model.")]
FORCE_OPT = Annotated[
    bool, typer.Option("--force", help="Overwrite the skill if already installed.")
]

MODEL_PRIORITY: list[Model] = ["claude", "codex", "gemini"]

TARGET_DIRS: dict[Model, str] = {
    "claude": ".claude/skills",
    "codex": ".codex/skills",
    "gemini": ".gemini/skills",
}

GLOB_CHARS = "*?["


def main(argv: list[str] | None = None) -> None:
    """Run the CLI with argv, or with sys.argv if argv is None."""
    app(argv)


def get_repo() -> SkillRepo:
    """
    Get the local skill repository, prepopulated with the built-in skills.
    """
    repo = SkillRepo(root=DEFAULT_SKILLS_ROOT)
    repo.init()
    return repo


@app.command(name="list")
def list_() -> None:
    """
    List all available skills.
    """
    repo = get_repo()

    for loader in repo.list_skills():
        for skill_dir in sorted(p for p in loader.path.iterdir() if p.is_dir()):
            try:
                skill = loader.load_skill(skill_dir.name)
            except FileNotFoundError:
                continue

            stdout.print(f"[bold blue]{loader.name}/{skill.name}[/]")
            rendered = Padding(skill.description, (0, 0, 0, 3))
            stdout.print(rendered)


@app.command()
def update(
    *,
    claude: CLAUDE_OPT = False,
    codex: CODEX_OPT = False,
    gemini: GEMINI_OPT = False,
) -> None:
    """
    Synchronize skills installed in the current directory with the latest
    versions from the skills repository. With no --claude/--codex/--gemini
    flags, every installed model directory found in the current directory is
    updated.
    """
    repo = get_repo()
    models = _select_models(claude=claude, codex=codex, gemini=gemini)

    had_error = False
    found_any = False
    for model in models:
        skills_dir = Path.cwd() / TARGET_DIRS[model]
        if not skills_dir.is_dir():
            continue

        for target_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            if not (target_dir / "SKILL.md").is_file():
                continue

            found_any = True
            name = target_dir.name
            matches = repo.find_skills(f"*/{name}")

            if not matches:
                stdout.print(f"* [bold]{name}[/] - [yellow]not found in repo[/yellow]")
                continue
            if len(matches) > 1:
                stderr.print(
                    f"[red]Ambiguous skill '{name}' matches: "
                    f"{', '.join(matches)}[/red]"
                )
                had_error = True
                continue

            fullname = matches[0]
            changed = _sync_skill(repo, fullname, target_dir)
            status, color = ("updated", "green") if changed else ("up to date", "blue")
            stdout.print(f"* [bold]{fullname}[/] - [{color}]{status}[/{color}]")

    if not found_any:
        stdout.print("No skills installed.")

    if had_error:
        raise typer.Exit(code=1)


@app.command()
def add(
    skill: Annotated[str, typer.Argument(...)],
    *,
    claude: CLAUDE_OPT = False,
    codex: CODEX_OPT = False,
    gemini: GEMINI_OPT = False,
    force: FORCE_OPT = False,
) -> None:
    """
    Add a new skill. The skill argument accepts glob patterns (e.g.
    "python/*") to install every matching skill at once. Pass --force to
    overwrite skills that are already installed.
    """
    model = _get_model(claude=claude, codex=codex, gemini=gemini)
    repo = get_repo()

    if _is_glob(skill):
        fullnames = repo.find_skills(skill)
        if not fullnames:
            stderr.print(f"[red]No skills match: {skill}[/red]")
            raise typer.Exit(code=1)

        had_error = False
        for fullname in fullnames:
            try:
                target_dir = _install_skill(repo, fullname, model=model, force=force)
            except FileExistsError:
                stdout.print(f"* [bold]{fullname}[/] - [yellow]skip[/yellow]")
                continue
            except ValueError as exc:
                stderr.print(f"[red]{exc}[/red]")
                had_error = True
                continue
            rel_path = target_dir.relative_to(Path.cwd())
            stdout.print(f"* [bold]{fullname}[/] - [green]{rel_path}[/green]")

        if had_error:
            raise typer.Exit(code=1)
        return

    fullname = repo._resolve_fullname(skill)
    try:
        target_dir = _install_skill(repo, fullname, model=model, force=force)
    except (ValueError, FileExistsError) as exc:
        stderr.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    stdout.print(f"Installed '{fullname}' to {_relpath(target_dir)}")


@app.command()
def edit(
    skill: Annotated[str, typer.Argument(...)],
    *,
    claude: CLAUDE_OPT = False,
    codex: CODEX_OPT = False,
    gemini: GEMINI_OPT = False,
) -> None:
    """
    Edit an existing skill.
    """
    _get_model(claude=claude, codex=codex, gemini=gemini)
    repo = get_repo()

    fullname = repo._resolve_fullname(skill)
    _, _, name = fullname.partition("/")
    try:
        loader = repo.get_skill(fullname)
    except ValueError as exc:
        stderr.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    skill_md = loader.path / name / "SKILL.md"
    editor = os.environ.get("EDITOR", "vi")
    subprocess.run([editor, str(skill_md)], check=True)


@app.command()
def new(
    skill: Annotated[str, typer.Argument(...)],
    *,
    claude: CLAUDE_OPT = False,
    codex: CODEX_OPT = False,
    gemini: GEMINI_OPT = False,
) -> None:
    """
    Create a new skill.
    """
    _get_model(claude=claude, codex=codex, gemini=gemini)
    repo = get_repo()

    category, sep, name = skill.partition("/")
    if not sep:
        stderr.print(
            f"[red]Invalid skill name: {skill}. Expected format: 'category/name'.[/red]"
        )
        raise typer.Exit(code=1)

    template = Skill(
        name=name,
        description="TODO: describe when this skill should be used.",
        source="# " + name + "\n\nTODO: write the skill content.\n",
    )
    try:
        repo.add_skill(skill, template, duplicate="raise")
    except FileExistsError as exc:
        stderr.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    skill_md = repo.root / category / name / "SKILL.md"
    editor = os.environ.get("EDITOR", "vi")
    subprocess.run([editor, str(skill_md)], check=True)
    stdout.print(f"Created new skill '{skill}' at {_relpath(skill_md)}")


#
# Utility functions
#
def _get_model(*, claude: bool, codex: bool, gemini: bool) -> Model:
    """
    Determine which model to use from the command-line flags.

    Returns the first model in MODEL_PRIORITY whose flag is set, or
    MODEL_PRIORITY[0] if none of them are.
    """
    flags = {"claude": claude, "codex": codex, "gemini": gemini}
    for model in MODEL_PRIORITY:
        if flags[model]:
            return model

    return MODEL_PRIORITY[0]


def _select_models(*, claude: bool, codex: bool, gemini: bool) -> list[Model]:
    """
    Determine which models' skill directories to operate on.

    Returns every model whose flag is set, or every model in MODEL_PRIORITY
    if none of the flags are set.
    """
    flags = {"claude": claude, "codex": codex, "gemini": gemini}
    selected = [model for model in MODEL_PRIORITY if flags[model]]
    return selected or list(MODEL_PRIORITY)


def _is_glob(pattern: str, /) -> bool:
    """Return whether pattern contains any glob metacharacters."""
    return any(ch in pattern for ch in GLOB_CHARS)


def _relpath(path: Path, /) -> str:
    """Format path relative to the current working directory, for display."""
    return os.path.relpath(path, Path.cwd())


def _install_skill(
    repo: SkillRepo, fullname: str, /, *, model: Model, force: bool = False
) -> Path:
    """
    Copy a skill from the repo into the current project.

    Raises:
        ValueError: if the skill isn't found in the repo.
        FileExistsError: if it's already installed and force is not set.
    """
    loader = repo.get_skill(fullname)
    _, _, name = fullname.partition("/")

    source_dir = loader.path / name
    target_dir = Path.cwd() / TARGET_DIRS[model] / name

    if target_dir.exists():
        if not force:
            msg = f"Skill already installed: {_relpath(target_dir)}"
            raise FileExistsError(msg)
        shutil.rmtree(target_dir)

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, target_dir)
    return target_dir


def _sync_skill(repo: SkillRepo, fullname: str, target_dir: Path, /) -> bool:
    """
    Overwrite target_dir with the repo's current contents of fullname.

    Returns whether target_dir's content changed.
    """
    loader = repo.get_skill(fullname)
    _, _, name = fullname.partition("/")
    source_dir = loader.path / name

    if _dirs_equal(source_dir, target_dir):
        return False

    shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)
    return True


def _dirs_equal(a: Path, b: Path, /) -> bool:
    """Recursively compare two directories by file name and content."""
    a_files = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
    b_files = sorted(p.relative_to(b) for p in b.rglob("*") if p.is_file())
    if a_files != b_files:
        return False
    return all((a / rel).read_bytes() == (b / rel).read_bytes() for rel in a_files)
