"""Tests for public CLI commands."""

from pathlib import Path

from kingdom_forge.cli import main


def test_validate_and_list_commands(project_yaml: Path, capsys: object) -> None:
    assert main(["--config", str(project_yaml), "validate"]) == 0
    assert main(["--config", str(project_yaml), "list"]) == 0
    assert "banner" in capsys.readouterr().out  # type: ignore[attr-defined]
