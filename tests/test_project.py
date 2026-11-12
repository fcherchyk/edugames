"""S1_AC1, S1_AC17, S1_AC18 and S3_AC17: platforms, asset licences, the sandbox demo and the
docs."""

import asyncio
import re
import tomllib
from pathlib import Path

import pygame
import pytest

from edugames import __main__ as entry
from edugames.core.content import ASSETS_DIR
from edugames.demo import run_demo
from edugames.ui import app as app_module

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "S1_mvp.md"
ALLOWED_LICENCES = ("SIL Open Font License", "Public domain", "MIT", "CC0")


def test_S1_AC1_the_game_has_a_command_and_supports_python_3_12() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert project["project"]["scripts"]["edugames"] == "edugames.__main__:main"
    assert project["project"]["requires-python"] == ">=3.12"
    assert callable(entry.main)


def test_S1_AC1_ci_runs_the_tests_on_mac_linux_and_windows() -> None:
    workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text()

    for system in ("macos-latest", "ubuntu-latest", "windows-latest"):
        assert system in workflow
    assert "uv run pytest" in workflow


def test_S1_AC1_the_app_opens_a_window_and_runs_its_loop(tmp_path, monkeypatch) -> None:
    app = app_module.create_app(tmp_path)
    assert app.surface.get_size() == (1280, 800)
    frames = []

    def one_frame():
        frames.append(1)
        app.running = len(frames) < 3
        return []

    monkeypatch.setattr(pygame.event, "get", one_frame)
    asyncio.run(app.run())

    assert len(frames) == 3


@pytest.fixture(scope="module")
def demo_shots(tmp_path_factory) -> list[Path]:
    """The sandbox demo's screenshots (played once for the tests that need them)."""
    folder = tmp_path_factory.mktemp("demo")
    return run_demo(folder / "screens", folder / "data")


def test_S1_AC1_the_sandbox_demo_saves_a_picture_of_every_screen(demo_shots) -> None:
    shots = demo_shots

    assert [p.stem.split("-", 1)[1] for p in shots][:9] == [
        "players",
        "name",
        "look",
        "home",
        "path",
        "memory",
        "victory",
        "path-after-win",
        "wardrobe",
    ]
    assert all(pygame.image.load(p).get_size() == (1280, 800) for p in shots)


def test_S3_AC17_the_demo_plays_letter_rain(demo_shots) -> None:
    assert [p.stem.split("-", 1)[1] for p in demo_shots][9:] == [
        "rain-path",
        "rain-letters",
        "rain-no-keyboard",
        "rain-victory",
        "rain-pictures",
        "rain-choices",
    ]


def test_S1_AC17_every_asset_is_credited_with_an_allowed_licence() -> None:
    credits = (ROOT / "CREDITS.md").read_text()
    sections = re.split(r"^## ", credits, flags=re.M)[1:]
    credited = {}
    for section in sections:
        licence = re.search(r"^Licence: (.+)$", section, re.M)
        assert licence, f"no licence in: {section.splitlines()[0]}"
        for path in re.findall(r"^- `([^`]+)`", section, re.M):
            credited[path] = licence[1]

    files = [p for p in ASSETS_DIR.rglob("*") if p.is_file() and p.name != ".DS_Store"]
    for file in files:
        path = file.relative_to(ASSETS_DIR).as_posix()
        match = next((pattern for pattern in credited if Path(path).match(pattern)), None)
        assert match, f"{path} is not in CREDITS.md"
        assert credited[match].startswith(ALLOWED_LICENCES), f"{path}: {credited[match]}"


# S1_AC18: each slice doc (docs/S<n>_*.md) lists exactly the tests that exist for that slice, and
# each criterion has tests.

DOCS = {int(re.match(r"S(\d+)_", p.name)[1]): p for p in (ROOT / "docs").glob("S*_*.md")}
TEST = re.compile(r"^def (test_\w+)", re.M)


def documented(slice_: int) -> dict[int, set[str]]:
    heading = re.compile(rf"^### S{slice_}_AC(\d+): ", re.M)
    sections = heading.split(DOCS[slice_].read_text())[1:]
    listed: dict[int, set[str]] = {}
    for number, body in zip(sections[::2], sections[1::2], strict=True):
        body = body.split("\n## ", 1)[0]
        listed[int(number)] = set(re.findall(r"^- `(.+)`$", body, re.M))
    return listed


def in_sources(slice_: int) -> dict[int, set[str]]:
    found: dict[int, set[str]] = {}
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        for name in TEST.findall(path.read_text()):
            for number in re.findall(rf"S{slice_}_AC(\d+)", name):
                found.setdefault(int(number), set()).add(f"tests/{path.name}::{name}")
    return found


def test_S1_AC18_every_slice_has_a_doc() -> None:
    assert sorted(DOCS) == [1, 2, 3]
    assert DOCS[1] == DOC


@pytest.mark.parametrize("slice_", sorted(DOCS))
def test_S1_AC18_every_acceptance_criterion_has_tests(slice_) -> None:
    listed = documented(slice_)

    assert sorted(listed) == list(range(1, len(listed) + 1)), f"criteria must be S{slice_}_AC1..n"
    assert [n for n, tests in listed.items() if not tests] == []


@pytest.mark.parametrize("slice_", sorted(DOCS))
def test_S1_AC18_the_doc_lists_exactly_the_tests_that_exist(slice_) -> None:
    listed, found = documented(slice_), in_sources(slice_)

    for number in sorted(set(listed) | set(found)):
        assert listed.get(number, set()) == found.get(number, set()), f"S{slice_}_AC{number}"


def test_S1_AC18_every_test_names_its_criterion() -> None:
    unnamed = [
        f"{path.name}::{name}"
        for path in (ROOT / "tests").glob("test_*.py")
        for name in TEST.findall(path.read_text())
        if not re.match(r"test_S(\d+)_AC\d+_", name)
        or int(re.match(r"test_S(\d+)", name)[1]) not in DOCS
    ]

    assert unnamed == []
