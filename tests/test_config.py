"""Tests for Kingdom Forge YAML configuration loading."""

from pathlib import Path

import pytest

from kingdom_forge.config import load_project_config
from kingdom_forge.exceptions import ConfigurationError


def test_load_project_config_resolves_project_paths(tmp_path: Path) -> None:
    config_directory = tmp_path / "config"
    config_directory.mkdir()
    config_path = config_directory / "project.yaml"
    config_path.write_text(
        """project:\n  name: Test Kingdom\n  output_directory: output\n  assets_directory: assets\nlogging:\n  level: debug\n""",
        encoding="utf-8",
    )

    config = load_project_config(config_path)

    assert config.project.name == "Test Kingdom"
    assert config.project.output_directory == tmp_path / "output"
    assert config.project.assets_directory == tmp_path / "assets"
    assert config.logging.level == "DEBUG"


def test_load_project_config_rejects_unknown_keys(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    config_path.write_text(
        """project:\n  name: Test Kingdom\n  output_directory: output\n  assets_directory: assets\n  typo: value\nlogging:\n  level: INFO\n""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Unknown key"):
        load_project_config(config_path)


def test_load_project_config_requires_existing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="does not exist"):
        load_project_config(tmp_path / "missing.yaml")

