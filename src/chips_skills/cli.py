import os
import shutil
import subprocess
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.padding import Padding

from .console import stderr, stdout
from .local_repo import DEFAULT_SKILLS_ROOT, Skill, SkillRepo
from .models import Model

app = typer.Typer()

CLAUDE_OPT = Annotated[bool, typer.Option("--claude", help="Force using Claude model.")]
CODEX_OPT = Annotated[bool, typer.Option("--codex", help="Force using Codex model.")]
GEMINI_OPT = Annotated[bool, typer.Option("--gemini", help="Force using Gemini model.")]

MODEL_PRIORITY: list[Model] = ["claude", "codex", "gemini"]

TARGET_DIRS: dict[Model, str] = {
    "claude": ".claude/skills",
    "codex": ".codex/skills",
    "gemini": ".gemini/skills",
}


def main(argv: list[str] | None = None) -> None:
    """
    Entry point for the CLI.
    """
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
def add(
    skill: Annotated[str, typer.Argument(...)],
    claude: CLAUDE_OPT = False,
    codex: CODEX_OPT = False,
    gemini: GEMINI_OPT = False,
) -> None:
    """
    Add a new skill.
    """
    model = get_model(locals())
    repo = get_repo()

    _, _, name = skill.partition("/")
    try:
        loader = repo.get_skill(skill)
    except ValueError as exc:
        stderr.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    source_dir = loader.path / name
    target_dir = Path.cwd() / TARGET_DIRS[model] / name

    if target_dir.exists():
        stderr.print(f"[red]Skill already installed: {target_dir}[/red]")
        raise typer.Exit(code=1)

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, target_dir)
    stdout.print(f"Installed '{skill}' to {target_dir}")


@app.command()
def edit(
    skill: Annotated[str, typer.Argument(...)],
    claude: CLAUDE_OPT = False,
    codex: CODEX_OPT = False,
    gemini: GEMINI_OPT = False,
) -> None:
    """
    Edit an existing skill.
    """
    get_model(locals())
    repo = get_repo()

    _, _, name = skill.partition("/")
    try:
        loader = repo.get_skill(skill)
    except ValueError as exc:
        stderr.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    skill_md = loader.path / name / "SKILL.md"
    editor = os.environ.get("EDITOR", "vi")
    subprocess.run([editor, str(skill_md)], check=True)


@app.command()
def new(
    skill: Annotated[str, typer.Argument(...)],
    claude: CLAUDE_OPT = False,
    codex: CODEX_OPT = False,
    gemini: GEMINI_OPT = False,
) -> None:
    """
    Create a new skill.
    """
    get_model(locals())
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
    stdout.print(f"Created new skill '{skill}' at {skill_md}")


def get_model(locals: dict[str, Any]) -> Model:
    """
    Determine the model to use based on the command-line options.
    """
    for model in MODEL_PRIORITY:
        if locals.get(model) is True:
            return model

    return MODEL_PRIORITY[0]
