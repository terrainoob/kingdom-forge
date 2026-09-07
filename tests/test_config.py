"""Tests for typed project configuration."""

from pathlib import Path

import pytest

from kingdom_forge.config import load_project_config
from kingdom_forge.exceptions import ConfigurationError


def test_loads_complete_project(project_yaml: Path, tmp_path: Path) -> None:
    config = load_project_config(project_yaml)
    assert config.project.output_directory == tmp_path / "output"
    assert config.templates[0].name == "banner"
    assert config.brand.palette["gold"] == "#E8BC55"


def test_rejects_unknown_template_field(project_yaml: Path) -> None:
    project_yaml.write_text(project_yaml.read_text(encoding="utf-8") + "    typo: nope\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="Unknown key"):
        load_project_config(project_yaml)


def test_rejects_duplicate_template_names(project_yaml: Path) -> None:
    text = project_yaml.read_text(encoding="utf-8")
    duplicate = "  - name: banner\n    kind: thumbnail\n    width: 10\n    height: 10\n    background_color: night\n"
    project_yaml.write_text(text.replace("templates:\n", "templates:\n" + duplicate), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="Duplicate"):
        load_project_config(project_yaml)
