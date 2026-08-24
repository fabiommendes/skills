from __future__ import annotations

import fnmatch
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

FRONTMATTER_DELIM = "---"

BUNDLED_SKILLS_ROOT = Path(__file__).resolve().parent / "skills"
DEFAULT_SKILLS_ROOT = Path.home() / ".local" / "share" / "skills"

DuplicatePolicy = Literal["ask", "raise", "overwrite", "skip"]


@dataclass
class SkillRepo:
    """
    Manage the local repository of skills.

    Usually under the user's home directory, e.g., ~/.local/share/skills.
    """

    root: Path

    def init(self) -> None:
        """Initialize the repository, prepopulating it with the built-in skills."""
        self.prepopulate(duplicates="skip")

    def prepopulate(self, *, duplicates: DuplicatePolicy = "raise") -> None:
        """
        Prepopulate the repository with the skills bundled with the package.
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

    def find_skills(self, pattern: str, /) -> list[str]:
        """
        Return every "category/name" fullname in the repo matching a glob
        pattern (e.g. "python/*" or "*/python-modules").
        """
        matches = []
        for loader in self.list_skills():
            for skill_dir in sorted(p for p in loader.path.iterdir() if p.is_dir()):
                if not (skill_dir / "SKILL.md").is_file():
                    continue
                fullname = f"{loader.name}/{skill_dir.name}"
                if fnmatch.fnmatch(fullname, pattern):
                    matches.append(fullname)
        return matches

    def get_skill(self, fullname: str, /) -> SkillLoader:
        """
        Get a skill loader by its full name.

        Raises:
            ValueError: if fullname isn't "category/name", or no matching
                skill exists in the repository.
        """
        fullname = self._resolve_fullname(fullname)
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
        self, fullname: str, skill: Skill, /, *, duplicate: DuplicatePolicy = "raise"
    ) -> None:
        """
        Add a new skill to the repository.

        Raises:
            ValueError: if fullname isn't "category/name", or duplicate isn't
                one of "ask", "raise", "overwrite" or "skip".
            FileExistsError: if the skill already exists and duplicate is "raise".
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

    #
    # Utility methods
    #
    def _resolve_fullname(self, fullname: str, /) -> str:
        """
        Resolve a possibly abbreviated skill name to its actual "category/name".

        If "category/name" doesn't exist but "category/category-name" does
        (e.g. "python/modules" for "python/python-modules"), return the
        latter. Otherwise return fullname unchanged.
        """
        category, sep, name = fullname.partition("/")
        if not sep:
            return fullname

        category_path = self.root / category
        if (category_path / name / "SKILL.md").is_file():
            return fullname

        prefixed_name = f"{category}-{name}"
        if (category_path / prefixed_name / "SKILL.md").is_file():
            return f"{category}/{prefixed_name}"

        return fullname


@dataclass
class Skill:
    name: str
    description: str
    source: str
    version: str | None = None

    def render(self) -> str:
        """
        Render the skill as a SKILL.md document (frontmatter + body).

        >>> Skill(name="foo", description="does foo", source="# foo").render()
        '---\\nname: foo\\ndescription: does foo\\n---\\n\\n# foo\\n'
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
        """Return the name of the skill loader."""
        return self.path.name

    def load_skill(self, skill_name: str, /) -> Skill:
        """
        Load a skill by its name.

        Raises:
            FileNotFoundError: if no SKILL.md exists for skill_name.
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


def _parse_frontmatter(text: str, /) -> tuple[dict[str, str], str]:
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
