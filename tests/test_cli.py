"""Tests for the Kingdom Forge command-line interface."""

from pathlib import Path

from kingdom_forge.cli import main


def test_validate_command_returns_success(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)

    assert main(["--config", str(config_path), "validate"]) == 0


def test_show_config_prints_normalized_configuration(tmp_path: Path, capsys: object) -> None:
    config_path = _write_config(tmp_path)

    assert main(["--config", str(config_path), "show-config"]) == 0

    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert '"name": "Test Kingdom"' in captured.out


def _write_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "project.yaml"
    config_path.write_text(
        """project:\n  name: Test Kingdom\n  output_directory: output\n  assets_directory: assets\nlogging:\n  level: INFO\n""",
        encoding="utf-8",
    )
    return config_path
