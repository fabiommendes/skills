from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

FRONTMATTER_DELIM = "---"

BUNDLED_SKILLS_ROOT = Path(__file__).resolve().parent / "skills"
DEFAULT_SKILLS_ROOT = Path.home() / ".local" / "share" / "skills"


@dataclass
class SkillRepo:
    """
    Manage the local repository of skills.

    Usually under the user's home directory, e.g., ~/.local/share/skills.
    """

    root: Path

    def init(self) -> None:
        """
        Initialize the repository.
        """
        self.prepopulate(duplicates="skip")

    def prepopulate(
        self, duplicates: Literal["ask", "raise", "overwrite", "skip"] = "raise"
    ) -> None:
        """
        Prepopulate the repository with default skills.
        """
        self.root.mkdir(parents=True, exist_ok=True)
        if not BUNDLED_SKILLS_ROOT.is_dir():
            return

        for category_dir in sorted(
            p for p in BUNDLED_SKILLS_ROOT.iterdir() if p.is_dir()
        ):
            loader = SkillLoader(path=category_dir)
            for skill_dir in sorted(p for p in category_dir.iterdir() if p.is_dir()):
                if not (skill_dir / "SKILL.md").is_file():
                    continue
                skill = loader.load_skill(skill_dir.name)
                fullname = f"{category_dir.name}/{skill_dir.name}"
                self.add_skill(fullname, skill, duplicate=duplicates)

    def list_skills(self) -> Iterable[SkillLoader]:
        """
        List all available skill categories in the repository.
        """
        if not self.root.is_dir():
            return []
        return [SkillLoader(path=p) for p in sorted(self.root.iterdir()) if p.is_dir()]

    def get_skill(self, fullname: str) -> SkillLoader:
        """
        Get a skill loader by its full name.
        """
        category, sep, name = fullname.partition("/")
        if not sep:
            msg = f"Invalid skill name: {fullname}. Expected format: 'category/name'."
            raise ValueError(msg)

        category_path = self.root / category
        if not (category_path / name / "SKILL.md").is_file():
            msg = f"Skill not found: {fullname}"
            raise ValueError(msg)

        return SkillLoader(path=category_path)

    def add_skill(
        self,
        fullname: str,
        skill: Skill,
        duplicate: Literal["ask", "raise", "overwrite", "skip"] = "raise",
    ) -> None:
        """
        Add a new skill to the repository.
        """
        category, sep, name = fullname.partition("/")
        if not sep:
            msg = f"Invalid skill name: {fullname}. Expected format: 'category/name'."
            raise ValueError(msg)

        skill_dir = self.root / category / name
        skill_md = skill_dir / "SKILL.md"

        if skill_md.exists():
            if duplicate == "raise":
                msg = f"Skill already exists: {fullname}"
                raise FileExistsError(msg)
            elif duplicate == "skip":
                return
            elif duplicate == "ask":
                answer = input(f"Skill '{fullname}' already exists. Overwrite? [y/N] ")
                if answer.strip().lower() not in ("y", "yes"):
                    return
            elif duplicate != "overwrite":
                msg = f"Invalid duplicate policy: {duplicate!r}"
                raise ValueError(msg)

        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_md.write_text(skill.render())


@dataclass
class Skill:
    name: str
    description: str
    source: str
    version: str | None = None

    def render(self) -> str:
        """
        Render the skill as a SKILL.md document (frontmatter + body).
        """
        header = [
            FRONTMATTER_DELIM,
            f"name: {self.name}",
            f"description: {self.description}",
        ]
        if self.version is not None:
            header.append(f"version: {self.version}")
        header.append(FRONTMATTER_DELIM)
        return "\n".join(header) + "\n\n" + self.source.strip("\n") + "\n"


@dataclass
class SkillLoader:
    """
    Load skills from a directory containing one subdirectory per skill.
    """

    path: Path

    @property
    def name(self) -> str:
        """
        Return the name of the skill loader.
        """
        return self.path.name

    def load_skill(self, skill_name: str) -> Skill:
        """
        Load a skill by its name.
        """
        skill_md = self.path / skill_name / "SKILL.md"
        if not skill_md.is_file():
            msg = f"Skill not found: {self.name}/{skill_name}"
            raise FileNotFoundError(msg)

        meta, body = _parse_frontmatter(skill_md.read_text())
        return Skill(
            name=meta.get("name", skill_name),
            description=meta.get("description", ""),
            source=body,
            version=meta.get("version"),
        )


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """
    Split a SKILL.md document into its YAML-ish frontmatter and body.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return {}, text

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONTMATTER_DELIM:
            meta = {}
            for header_line in lines[1:i]:
                key, sep, value = header_line.partition(":")
                if sep:
                    meta[key.strip()] = value.strip()
            body = "\n".join(lines[i + 1 :]).strip("\n")
            return meta, body

    return {}, text
