"""Typed loading and validation for Kingdom Forge project configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import yaml

from kingdom_forge.exceptions import ConfigurationError

_ROOT_KEYS: Final[frozenset[str]] = frozenset({"project", "logging"})
_PROJECT_KEYS: Final[frozenset[str]] = frozenset(
    {"name", "output_directory", "assets_directory"}
)
_LOGGING_KEYS: Final[frozenset[str]] = frozenset({"level"})


@dataclass(frozen=True, slots=True)
class ProjectSettings:
    """Filesystem and identity settings for one Forge project."""

    name: str
    output_directory: Path
    assets_directory: Path


@dataclass(frozen=True, slots=True)
class LoggingSettings:
    """Logging settings controlled by project configuration."""

    level: str


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Validated configuration required to initialize Kingdom Forge."""

    project: ProjectSettings
    logging: LoggingSettings
    source_path: Path


def load_project_config(path: Path) -> ProjectConfig:
    """Load and validate a YAML project configuration from *path*.

    Relative asset and output paths are resolved relative to the configuration file.
    """
    source_path = path.resolve()
    if not source_path.is_file():
        raise ConfigurationError(f"Configuration file does not exist: {source_path}")

    try:
        with source_path.open(encoding="utf-8") as stream:
            document = yaml.safe_load(stream)
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Invalid YAML in {source_path}: {error}") from error

    root = _mapping(document, "document")
    _reject_unknown_keys(root, _ROOT_KEYS, "document")
    project = _mapping(root.get("project"), "project")
    logging = _mapping(root.get("logging"), "logging")
    _reject_unknown_keys(project, _PROJECT_KEYS, "project")
    _reject_unknown_keys(logging, _LOGGING_KEYS, "logging")

    base_directory = source_path.parent.parent
    return ProjectConfig(
        project=ProjectSettings(
            name=_non_empty_string(project.get("name"), "project.name"),
            output_directory=_resolve_directory(
                project.get("output_directory"), "project.output_directory", base_directory
            ),
            assets_directory=_resolve_directory(
                project.get("assets_directory"), "project.assets_directory", base_directory
            ),
        ),
        logging=LoggingSettings(level=_log_level(logging.get("level"))),
        source_path=source_path,
    )


def _mapping(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError(f"{location} must be a YAML mapping.")
    if not all(isinstance(key, str) for key in value):
        raise ConfigurationError(f"{location} must use string keys.")
    return value


def _reject_unknown_keys(
    mapping: dict[str, Any], allowed_keys: frozenset[str], location: str
) -> None:
    unknown_keys = sorted(set(mapping) - allowed_keys)
    if unknown_keys:
        formatted_keys = ", ".join(unknown_keys)
        raise ConfigurationError(f"Unknown key(s) in {location}: {formatted_keys}")


def _non_empty_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{location} must be a non-empty string.")
    return value.strip()


def _resolve_directory(value: Any, location: str, base_directory: Path) -> Path:
    directory = Path(_non_empty_string(value, location))
    return directory if directory.is_absolute() else (base_directory / directory).resolve()


def _log_level(value: Any) -> str:
    level = _non_empty_string(value, "logging.level").upper()
    valid_levels = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
    if level not in valid_levels:
        choices = ", ".join(sorted(valid_levels))
        raise ConfigurationError(f"logging.level must be one of: {choices}.")
    return level

