"""Command-line interface for validating and publishing Kingdom Forge projects."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Sequence

from kingdom_forge.config import ProjectConfig, load_project_config
from kingdom_forge.exceptions import ConfigurationError, KingdomForgeError
from kingdom_forge.logging import configure_logging
from kingdom_forge.publishing import Publisher

DEFAULT_CONFIG_PATH = Path(os.environ.get("KINGDOM_FORGE_CONFIG", "config/project.yaml"))
LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Create the Kingdom Forge argument parser."""
    parser = argparse.ArgumentParser(prog="kingdom-forge", description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Project YAML path.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="Validate project configuration.")
    commands.add_parser("show-config", help="Print normalized configuration.")
    build = commands.add_parser("build", help="Render configured graphics.")
    build.add_argument("--template", action="append", dest="templates", help="Template name; repeat to select multiple.")
    build.add_argument("--guides", action="store_true", help="Render safe-area guides where applicable.")
    commands.add_parser("list", help="List configured templates.")
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit status."""
    parser = build_parser()
    namespace = parser.parse_args(arguments)
    try:
        config = load_project_config(namespace.config)
        configure_logging(config.logging.level)
        if namespace.command == "validate":
            Publisher(config).validate()
            LOGGER.info("Validated configuration: %s", config.source_path)
        elif namespace.command == "show-config":
            print(json.dumps(_as_json(config), indent=2, sort_keys=True))
        elif namespace.command == "list":
            for template in config.templates:
                print(f"{template.name}\t{template.kind}\t{template.width}x{template.height}")
        elif namespace.command == "build":
            report = Publisher(config).build(set(namespace.templates) if namespace.templates else None, namespace.guides)
            LOGGER.info("Built %d artifact(s), version %s.", len(report.artifacts), report.version)
    except (ConfigurationError, KingdomForgeError, ValueError) as error:
        parser.error(str(error))
    return 0


def _as_json(config: ProjectConfig) -> dict[str, object]:
    return {
        "project": {"name": config.project.name, "version": config.project.version, "output_directory": str(config.project.output_directory), "assets_directory": str(config.project.assets_directory)},
        "logging": {"level": config.logging.level},
        "brand": {"palette": dict(config.brand.palette), "typography": dict(config.brand.typography), "spacing": dict(config.brand.spacing), "corner_radius": config.brand.corner_radius},
        "templates": [template.name for template in config.templates], "source_path": str(config.source_path),
    }
