"""Typed loading and validation for Kingdom Forge project configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from kingdom_forge.exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class ProjectSettings:
    """Project identity and filesystem locations."""
    name: str
    output_directory: Path
    assets_directory: Path
    version: str


@dataclass(frozen=True, slots=True)
class LoggingSettings:
    """Application logging settings."""
    level: str


@dataclass(frozen=True, slots=True)
class BrandSettings:
    """Brand tokens used by every template."""
    palette: Mapping[str, str]
    typography: Mapping[str, str]
    spacing: Mapping[str, int]
    corner_radius: int


@dataclass(frozen=True, slots=True)
class MottoLine:
    """A two-tone phrase used in a compact campaign motto."""
    lead: str
    accent: str
    accent_color: str


@dataclass(frozen=True, slots=True)
class MottoSettings:
    """Two-line, brand-token-driven motto treatment."""
    first: MottoLine
    second: MottoLine


@dataclass(frozen=True, slots=True)
class TemplateSettings:
    """Declarative settings for one rendered template."""
    name: str
    kind: str
    width: int
    height: int
    background_color: str
    headline: str = ""
    subtitle: str = ""
    tagline: str = ""
    logo: str | None = None
    character: str | None = None
    safe_area: str | None = None
    transparent: bool = False
    output_name: str | None = None
    background_image: str | None = None
    background_opacity: float = 1.0
    logo_scale: float = 0.25
    logo_anchor: str = "top_left"
    copy_width: float = 1.0
    copy_anchor: str = "full"
    copy_offset_y: int = 0
    copy_layout: str = "legacy"
    motto: MottoSettings | None = None
    motto_rotation_degrees: int = 0
    character_scale: float = 1.0


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Validated source of truth for a Kingdom Forge project."""
    project: ProjectSettings
    logging: LoggingSettings
    brand: BrandSettings
    templates: tuple[TemplateSettings, ...]
    source_path: Path


def load_project_config(path: Path) -> ProjectConfig:
    """Load YAML configuration and reject malformed or misspelled fields."""
    source_path = path.resolve()
    if not source_path.is_file():
        raise ConfigurationError(f"Configuration file does not exist: {source_path}")
    try:
        with source_path.open(encoding="utf-8") as stream:
            raw = yaml.safe_load(stream)
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Invalid YAML in {source_path}: {error}") from error
    root = _mapping(raw, "document")
    _unknown(root, {"project", "logging", "brand", "templates"}, "document")
    base = source_path.parent.parent if source_path.parent.name == "config" else source_path.parent
    project = _mapping(root.get("project"), "project")
    _unknown(project, {"name", "output_directory", "assets_directory", "version"}, "project")
    logging = _mapping(root.get("logging", {"level": "INFO"}), "logging")
    _unknown(logging, {"level"}, "logging")
    brand = _mapping(root.get("brand"), "brand")
    _unknown(brand, {"palette", "typography", "spacing", "corner_radius"}, "brand")
    result = ProjectConfig(
        project=ProjectSettings(_string(project.get("name"), "project.name"), _path(project.get("output_directory"), "project.output_directory", base), _path(project.get("assets_directory"), "project.assets_directory", base), _string(project.get("version", "0.1.0"), "project.version")),
        logging=LoggingSettings(_level(logging.get("level", "INFO"))),
        brand=_brand(brand), templates=_templates(root.get("templates", [])), source_path=source_path,
    )
    _unique_template_names(result.templates)
    return result


def _brand(raw: dict[str, Any]) -> BrandSettings:
    palette = _string_mapping(raw.get("palette"), "brand.palette")
    for name, color in palette.items():
        if not _is_color(color):
            raise ConfigurationError(f"brand.palette.{name} must be #RRGGBB or #RRGGBBAA.")
    typography = _string_mapping(raw.get("typography"), "brand.typography")
    spacing_raw = _mapping(raw.get("spacing"), "brand.spacing")
    spacing = {key: _positive_int(value, f"brand.spacing.{key}") for key, value in spacing_raw.items()}
    return BrandSettings(palette, typography, spacing, _non_negative_int(raw.get("corner_radius", 0), "brand.corner_radius"))


def _templates(raw: Any) -> tuple[TemplateSettings, ...]:
    if not isinstance(raw, list):
        raise ConfigurationError("templates must be a YAML list.")
    allowed = {"name", "kind", "width", "height", "background_color", "background_image", "background_opacity", "headline", "subtitle", "tagline", "logo", "logo_scale", "logo_anchor", "copy_width", "copy_anchor", "copy_offset_y", "copy_layout", "motto", "motto_rotation_degrees", "character", "character_scale", "safe_area", "transparent", "output_name"}
    result: list[TemplateSettings] = []
    for index, value in enumerate(raw):
        item = _mapping(value, f"templates[{index}]")
        _unknown(item, allowed, f"templates[{index}]")
        result.append(TemplateSettings(
            _string(item.get("name"), f"templates[{index}].name"), _string(item.get("kind"), f"templates[{index}].kind"), _positive_int(item.get("width"), f"templates[{index}].width"), _positive_int(item.get("height"), f"templates[{index}].height"), _string(item.get("background_color"), f"templates[{index}].background_color"),
            _optional_string(item.get("headline"), f"templates[{index}].headline"), _optional_string(item.get("subtitle"), f"templates[{index}].subtitle"), _optional_string(item.get("tagline"), f"templates[{index}].tagline"), _optional_path(item.get("logo"), f"templates[{index}].logo"), _optional_path(item.get("character"), f"templates[{index}].character"), _optional_string(item.get("safe_area"), f"templates[{index}].safe_area"), _bool(item.get("transparent", False), f"templates[{index}].transparent"), _optional_string(item.get("output_name"), f"templates[{index}].output_name"), _optional_path(item.get("background_image"), f"templates[{index}].background_image"), _opacity(item.get("background_opacity", 1.0), f"templates[{index}].background_opacity"), _positive_unit_float(item.get("logo_scale", 0.25), f"templates[{index}].logo_scale"), _logo_anchor(item.get("logo_anchor", "top_left"), f"templates[{index}].logo_anchor"), _positive_unit_float(item.get("copy_width", 1.0), f"templates[{index}].copy_width"), _copy_anchor(item.get("copy_anchor", "full"), f"templates[{index}].copy_anchor"), _integer(item.get("copy_offset_y", 0), f"templates[{index}].copy_offset_y"), _copy_layout(item.get("copy_layout", "legacy"), f"templates[{index}].copy_layout"), _motto(item.get("motto"), f"templates[{index}].motto"), _integer(item.get("motto_rotation_degrees", 0), f"templates[{index}].motto_rotation_degrees"), _positive_unit_float(item.get("character_scale", 1.0), f"templates[{index}].character_scale"),
        ))
    return tuple(result)


def _mapping(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ConfigurationError(f"{location} must be a YAML mapping with string keys.")
    return value


def _string_mapping(value: Any, location: str) -> dict[str, str]:
    return {key: _string(item, f"{location}.{key}") for key, item in _mapping(value, location).items()}


def _positive_unit_float(value: Any, location: str) -> float:
    result = _opacity(value, location)
    if result == 0:
        raise ConfigurationError(f"{location} must be greater than zero and at most one.")
    return result


def _logo_anchor(value: Any, location: str) -> str:
    result = _string(value, location)
    if result not in {"top_left", "top_center", "center"}:
        raise ConfigurationError(f"{location} must be one of: top_left, top_center, center.")
    return result


def _copy_anchor(value: Any, location: str) -> str:
    result = _string(value, location)
    if result not in {"full", "left"}:
        raise ConfigurationError(f"{location} must be one of: full, left.")
    return result


def _copy_layout(value: Any, location: str) -> str:
    result = _string(value, location)
    if result not in {"legacy", "stacked"}:
        raise ConfigurationError(f"{location} must be one of: legacy, stacked.")
    return result


def _motto(value: Any, location: str) -> MottoSettings | None:
    if value is None:
        return None
    raw = _mapping(value, location)
    _unknown(raw, {"first", "second"}, location)
    return MottoSettings(_motto_line(raw.get("first"), f"{location}.first"), _motto_line(raw.get("second"), f"{location}.second"))


def _motto_line(value: Any, location: str) -> MottoLine:
    raw = _mapping(value, location)
    _unknown(raw, {"lead", "accent", "accent_color"}, location)
    return MottoLine(_string(raw.get("lead"), f"{location}.lead"), _string(raw.get("accent"), f"{location}.accent"), _string(raw.get("accent_color"), f"{location}.accent_color"))


def _unknown(value: dict[str, Any], allowed: set[str], location: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ConfigurationError(f"Unknown key(s) in {location}: {', '.join(unknown)}")


def _string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{location} must be a non-empty string.")
    return value.strip()


def _optional_string(value: Any, location: str) -> str:
    return "" if value is None else _string(value, location)


def _optional_path(value: Any, location: str) -> str | None:
    return None if value is None else _string(value, location)


def _positive_int(value: Any, location: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigurationError(f"{location} must be a positive integer.")
    return value


def _non_negative_int(value: Any, location: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ConfigurationError(f"{location} must be a non-negative integer.")
    return value


def _integer(value: Any, location: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ConfigurationError(f"{location} must be an integer.")
    return value


def _bool(value: Any, location: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigurationError(f"{location} must be true or false.")
    return value


def _opacity(value: Any, location: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise ConfigurationError(f"{location} must be a number from 0 through 1.")
    return float(value)


def _path(value: Any, location: str, base: Path) -> Path:
    candidate = Path(_string(value, location))
    return candidate if candidate.is_absolute() else (base / candidate).resolve()


def _level(value: Any) -> str:
    level = _string(value, "logging.level").upper()
    if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ConfigurationError("logging.level must be a standard Python log level.")
    return level


def _is_color(value: str) -> bool:
    return len(value) in {7, 9} and value.startswith("#") and all(char in "0123456789abcdefABCDEF" for char in value[1:])


def _unique_template_names(templates: tuple[TemplateSettings, ...]) -> None:
    names = [template.name for template in templates]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ConfigurationError(f"Duplicate template name(s): {', '.join(duplicates)}")
