"""Pillow-based canvas, layers, typography, and PNG export primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from kingdom_forge.layout import Rect


def parse_color(value: str) -> tuple[int, int, int, int]:
    """Convert a CSS-like hexadecimal color to an RGBA tuple."""
    value = value.lstrip("#")
    if len(value) == 6:
        value += "ff"
    return tuple(int(value[index:index + 2], 16) for index in range(0, 8, 2))  # type: ignore[return-value]


@dataclass(slots=True)
class Canvas:
    """An RGBA image canvas with safe compositing operations."""
    width: int
    height: int
    color: tuple[int, int, int, int]
    image: Image.Image = field(init=False)

    def __post_init__(self) -> None:
        self.image = Image.new("RGBA", (self.width, self.height), self.color)

    def paste(self, image: Image.Image, bounds: Rect) -> None:
        """Scale and alpha-composite an image into *bounds*."""
        resized = image.resize((bounds.width, bounds.height), Image.Resampling.LANCZOS)
        self.image.alpha_composite(resized, (bounds.x, bounds.y))

    def cover(self, image: Image.Image, opacity: float = 1.0) -> None:
        """Fill the canvas with an aspect-preserving image at the requested opacity."""
        if not 0.0 <= opacity <= 1.0:
            raise ValueError("Background opacity must be between 0 and 1.")
        fitted = ImageOps.fit(image.convert("RGBA"), (self.width, self.height), Image.Resampling.LANCZOS)
        if opacity < 1.0:
            fitted.putalpha(fitted.getchannel("A").point(lambda value: round(value * opacity)))
        self.image.alpha_composite(fitted)


@dataclass(frozen=True, slots=True)
class Layer:
    """A named, ordered image layer ready to composite onto a canvas."""
    name: str
    image: Image.Image
    bounds: Rect
    opacity: float = 1.0


class Renderer:
    """Composites ordered layers while retaining Pillow as the canonical image type."""
    def render(self, canvas: Canvas, layers: list[Layer]) -> Canvas:
        """Apply layers in the supplied order and return the canvas."""
        for layer in layers:
            if not 0.0 <= layer.opacity <= 1.0:
                raise ValueError(f"Layer opacity must be between 0 and 1: {layer.name}")
            image = layer.image.copy()
            if layer.opacity < 1.0:
                alpha = image.getchannel("A").point(lambda value: round(value * layer.opacity))
                image.putalpha(alpha)
            canvas.paste(image, layer.bounds)
        return canvas


class FontLoader:
    """Loads configured fonts once and falls back to Pillow's portable default."""
    def __init__(self) -> None:
        self._cache: dict[tuple[str, int], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}

    def get(self, source: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Return a cached font at the requested size."""
        key = (source, size)
        if key not in self._cache:
            try:
                self._cache[key] = ImageFont.truetype(source, size)
            except OSError:
                self._cache[key] = ImageFont.load_default(size=size)
        return self._cache[key]


class TextPainter:
    """Measures and paints text with constraint-derived alignment."""
    def __init__(self, fonts: FontLoader) -> None:
        self._fonts = fonts

    def centered(self, canvas: Canvas, text: str, area: Rect, font_name: str, size: int, color: tuple[int, int, int, int], y_offset: int = 0) -> None:
        """Paint text horizontally centered in *area*."""
        if not text:
            return
        draw = ImageDraw.Draw(canvas.image)
        font = self._fonts.get(font_name, size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        x = area.center[0] - (right - left) // 2
        y = area.center[1] - (bottom - top) // 2 + y_offset
        draw.text((x, y), text, font=font, fill=color)


class PngExporter:
    """Exports canvases atomically as optimized PNG files."""
    def export(self, canvas: Canvas, destination: Path) -> Path:
        """Write a PNG, creating parent folders and replacing the target atomically."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(".tmp.png")
        canvas.image.save(temporary, format="PNG", optimize=True)
        temporary.replace(destination)
        return destination
