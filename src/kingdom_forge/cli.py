"""Command-line interface for validating Kingdom Forge projects."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Sequence

from kingdom_forge.config import ProjectConfig, load_project_config
from kingdom_forge.exceptions import ConfigurationError
from kingdom_forge.logging import configure_logging

DEFAULT_CONFIG_PATH = Path("config/project.yaml")
LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Create the Kingdom Forge argument parser."""
    parser = argparse.ArgumentParser(prog="kingdom-forge", description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to a project YAML file."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate", help="Validate a project configuration.")
    subcommands.add_parser("show-config", help="Print normalized project configuration as JSON.")
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit status."""
    parser = build_parser()
    namespace = parser.parse_args(arguments)
    try:
        config = load_project_config(namespace.config)
    except ConfigurationError as error:
        parser.error(str(error))

    configure_logging(config.logging.level)
    if namespace.command == "validate":
        LOGGER.info("Validated configuration: %s", config.source_path)
    elif namespace.command == "show-config":
        print(json.dumps(_as_json(config), indent=2, sort_keys=True))
    return 0


def _as_json(config: ProjectConfig) -> dict[str, object]:
    return {
        "project": {
            "name": config.project.name,
            "output_directory": str(config.project.output_directory),
            "assets_directory": str(config.project.assets_directory),
        },
        "logging": {"level": config.logging.level},
        "source_path": str(config.source_path),
    }

