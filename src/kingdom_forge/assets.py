"""Asset discovery, metadata validation, and immutable image caching."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image

from kingdom_forge.exceptions import KingdomForgeError


class AssetError(KingdomForgeError):
    """Raised when an asset cannot be resolved or read."""


@dataclass(frozen=True, slots=True)
class AssetMetadata:
    """Metadata recorded beside an asset as a YAML document in future workflows."""
    path: Path
    digest: str
    tags: tuple[str, ...] = ()


class AssetManager:
    """Resolve project-relative assets and cache decoded RGBA images."""
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._cache: dict[Path, Image.Image] = {}

    def resolve(self, relative_path: str) -> Path:
        """Resolve an asset path without allowing it to escape the asset root."""
        candidate = (self._root / relative_path).resolve()
        if self._root not in candidate.parents and candidate != self._root:
            raise AssetError(f"Asset path escapes asset root: {relative_path}")
        if not candidate.is_file():
            raise AssetError(f"Missing asset: {candidate}")
        return candidate

    def image(self, relative_path: str) -> Image.Image:
        """Load an RGBA image, returning a defensive copy of the cached source."""
        path = self.resolve(relative_path)
        if path not in self._cache:
            try:
                with Image.open(path) as source:
                    self._cache[path] = source.convert("RGBA")
            except OSError as error:
                raise AssetError(f"Unable to read image asset {path}: {error}") from error
        return self._cache[path].copy()

    def inventory(self) -> tuple[AssetMetadata, ...]:
        """Return a deterministic hash inventory for all source assets."""
        files = sorted(path for path in self._root.rglob("*") if path.is_file()) if self._root.exists() else []
        return tuple(AssetMetadata(path.relative_to(self._root), sha256(path.read_bytes()).hexdigest()) for path in files)
