from __future__ import annotations

from pathlib import Path

import pytest

from chips_skills.local_repo import Skill, SkillLoader, SkillRepo


def write_skill(
    dir_: Path, category: str, name: str, description: str = "desc"
) -> Path:
    skill_dir = dir_ / category / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n\nBody text.\n"
    )
    return skill_md


class TestSkill:
    def test_render_round_trips_through_load_skill(self, tmp_path: Path) -> None:
        skill = Skill(
            name="foo", description="does foo things", source="# foo\n\nBody."
        )
        category_dir = tmp_path / "cat"
        skill_dir = category_dir / "foo"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(skill.render())

        loaded = SkillLoader(path=category_dir).load_skill("foo")

        assert loaded.name == "foo"
        assert loaded.description == "does foo things"
        assert loaded.source == "# foo\n\nBody."

    def test_render_includes_version_when_set(self) -> None:
        skill = Skill(name="foo", description="d", source="body", version="1.0")
        assert "version: 1.0" in skill.render()

    def test_render_omits_version_when_unset(self) -> None:
        skill = Skill(name="foo", description="d", source="body")
        assert "version:" not in skill.render()


class TestSkillLoader:
    def test_load_skill_reads_frontmatter_and_body(self, tmp_path: Path) -> None:
        write_skill(tmp_path, "python", "my-skill", description="Does a thing")
        loader = SkillLoader(path=tmp_path / "python")

        skill = loader.load_skill("my-skill")

        assert skill.name == "my-skill"
        assert skill.description == "Does a thing"
        assert "Body text." in skill.source

    def test_name_returns_directory_name(self, tmp_path: Path) -> None:
        loader = SkillLoader(path=tmp_path / "python")
        assert loader.name == "python"

    def test_load_skill_missing_raises(self, tmp_path: Path) -> None:
        (tmp_path / "python").mkdir()
        loader = SkillLoader(path=tmp_path / "python")

        with pytest.raises(FileNotFoundError):
            loader.load_skill("does-not-exist")


class TestSkillRepo:
    def test_add_and_get_skill(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        skill = Skill(name="my-skill", description="d", source="body")

        repo.add_skill("python/my-skill", skill)
        loader = repo.get_skill("python/my-skill")

        assert loader.load_skill("my-skill").description == "d"

    def test_get_skill_requires_category_slash_name(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        with pytest.raises(ValueError):
            repo.get_skill("no-slash-here")

    def test_get_skill_missing_raises(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        with pytest.raises(ValueError):
            repo.get_skill("python/does-not-exist")

    def test_get_skill_matches_category_prefixed_abbreviation(
        self, tmp_path: Path
    ) -> None:
        repo = SkillRepo(root=tmp_path)
        repo.add_skill(
            "python/python-modules",
            Skill(name="python-modules", description="d", source="s"),
        )

        loader = repo.get_skill("python/modules")

        assert loader.load_skill("python-modules").name == "python-modules"

    def test_resolve_fullname_prefers_exact_match(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        repo.add_skill(
            "python/modules", Skill(name="modules", description="d", source="s")
        )
        repo.add_skill(
            "python/python-modules",
            Skill(name="python-modules", description="d", source="s"),
        )

        assert repo._resolve_fullname("python/modules") == "python/modules"

    def test_resolve_fullname_abbreviated_match(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        repo.add_skill(
            "python/python-modules",
            Skill(name="python-modules", description="d", source="s"),
        )

        assert repo._resolve_fullname("python/modules") == "python/python-modules"

    def test_resolve_fullname_returns_unchanged_when_no_match(
        self, tmp_path: Path
    ) -> None:
        repo = SkillRepo(root=tmp_path)
        assert (
            repo._resolve_fullname("python/does-not-exist") == "python/does-not-exist"
        )

    def test_resolve_fullname_returns_unchanged_without_slash(
        self, tmp_path: Path
    ) -> None:
        repo = SkillRepo(root=tmp_path)
        assert repo._resolve_fullname("no-slash-here") == "no-slash-here"

    def test_add_skill_duplicate_raise(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        skill = Skill(name="my-skill", description="d", source="body")
        repo.add_skill("python/my-skill", skill)

        with pytest.raises(FileExistsError):
            repo.add_skill("python/my-skill", skill)

    def test_add_skill_duplicate_skip_keeps_original(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        repo.add_skill(
            "python/my-skill", Skill(name="my-skill", description="v1", source="a")
        )
        repo.add_skill(
            "python/my-skill",
            Skill(name="my-skill", description="v2", source="b"),
            duplicate="skip",
        )

        assert (
            repo.get_skill("python/my-skill").load_skill("my-skill").description == "v1"
        )

    def test_add_skill_duplicate_overwrite_replaces(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        repo.add_skill(
            "python/my-skill", Skill(name="my-skill", description="v1", source="a")
        )
        repo.add_skill(
            "python/my-skill",
            Skill(name="my-skill", description="v2", source="b"),
            duplicate="overwrite",
        )

        assert (
            repo.get_skill("python/my-skill").load_skill("my-skill").description == "v2"
        )

    def test_add_skill_invalid_fullname_raises(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        with pytest.raises(ValueError):
            repo.add_skill("no-slash", Skill(name="x", description="d", source="s"))

    def test_list_skills_returns_one_loader_per_category(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        repo.add_skill("python/a", Skill(name="a", description="d", source="s"))
        repo.add_skill("python/b", Skill(name="b", description="d", source="s"))
        repo.add_skill("generic/c", Skill(name="c", description="d", source="s"))

        names = sorted(loader.name for loader in repo.list_skills())

        assert names == ["generic", "python"]

    def test_list_skills_on_missing_root_returns_empty(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path / "does-not-exist")
        assert list(repo.list_skills()) == []

    def test_prepopulate_copies_bundled_skills(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        repo.prepopulate(duplicates="skip")

        loaders = {loader.name: loader for loader in repo.list_skills()}
        assert "python" in loaders
        skill = loaders["python"].load_skill("python-functions")
        assert skill.name == "python-functions"
        assert skill.description

    def test_init_is_idempotent(self, tmp_path: Path) -> None:
        repo = SkillRepo(root=tmp_path)
        repo.init()
        repo.init()  # should not raise on duplicates

        loaders = {loader.name: loader for loader in repo.list_skills()}
        assert "python" in loaders
