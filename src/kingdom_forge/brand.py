"""Brand token resolution and source-asset validation."""

from __future__ import annotations

from dataclasses import dataclass

from kingdom_forge.assets import AssetManager, AssetMetadata
from kingdom_forge.config import BrandSettings
from kingdom_forge.exceptions import ConfigurationError
from kingdom_forge.render import parse_color


@dataclass(frozen=True, slots=True)
class AssetValidationReport:
    """Results from inspecting configured source assets."""
    assets: tuple[AssetMetadata, ...]
    duplicate_digests: tuple[str, ...]


class BrandSystem:
    """Central brand facade for named colors, fonts, and asset health checks."""
    def __init__(self, settings: BrandSettings, assets: AssetManager) -> None:
        self.settings = settings
        self.assets = assets

    def color(self, token: str) -> tuple[int, int, int, int]:
        """Resolve a palette token or explicit configured hexadecimal color."""
        try:
            return parse_color(self.settings.palette.get(token, token))
        except ValueError as error:
            raise ConfigurationError(f"Unknown or invalid color token: {token}") from error

    def font(self, role: str) -> str:
        """Resolve a configured typography role."""
        try:
            return self.settings.typography[role]
        except KeyError as error:
            raise ConfigurationError(f"Unknown typography role: {role}") from error

    def validate_assets(self) -> AssetValidationReport:
        """Inventory assets and report byte-identical duplicates by digest."""
        assets = self.assets.inventory()
        digests = [asset.digest for asset in assets]
        duplicates = tuple(sorted({digest for digest in digests if digests.count(digest) > 1}))
        return AssetValidationReport(assets, duplicates)
