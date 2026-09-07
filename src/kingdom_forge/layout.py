"""Constraint-oriented geometry primitives and reusable platform safe areas."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class Rect:
    """An integer rectangle with derived anchor coordinates."""
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        """Return the exclusive right edge."""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Return the exclusive bottom edge."""
        return self.y + self.height

    @property
    def center(self) -> tuple[int, int]:
        """Return the center anchor."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    def inset(self, amount: int) -> "Rect":
        """Return a rectangle inset equally on every edge."""
        return Rect(self.x + amount, self.y + amount, self.width - 2 * amount, self.height - 2 * amount)


class Anchor(StrEnum):
    """Named anchors understood by the layout engine."""
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTER_X = "center_x"
    CENTER_Y = "center_y"


@dataclass(frozen=True, slots=True)
class Constraints:
    """Constraint-based placement relative to a containing rectangle."""
    width: int
    height: int
    horizontal: Anchor = Anchor.CENTER_X
    vertical: Anchor = Anchor.CENTER_Y
    offset_x: int = 0
    offset_y: int = 0

    def resolve(self, container: Rect) -> Rect:
        """Resolve this placement against *container*."""
        x = {Anchor.LEFT: container.x, Anchor.RIGHT: container.right - self.width, Anchor.CENTER_X: container.center[0] - self.width // 2}.get(self.horizontal)
        y = {Anchor.TOP: container.y, Anchor.BOTTOM: container.bottom - self.height, Anchor.CENTER_Y: container.center[1] - self.height // 2}.get(self.vertical)
        if x is None or y is None:
            raise ValueError("Constraints require one horizontal and one vertical anchor.")
        return Rect(x + self.offset_x, y + self.offset_y, self.width, self.height)


@dataclass(frozen=True, slots=True)
class Container:
    """A padded layout container that can distribute child rectangles in rows or columns."""
    bounds: Rect
    padding: int = 0
    gap: int = 0

    @property
    def content(self) -> Rect:
        """Return the usable content rectangle after padding."""
        return self.bounds.inset(self.padding)

    def row(self, widths: list[int], height: int, vertical: Anchor = Anchor.CENTER_Y) -> tuple[Rect, ...]:
        """Lay out widths from left to right with configured gaps."""
        required = sum(widths) + self.gap * max(0, len(widths) - 1)
        if required > self.content.width or height > self.content.height:
            raise ValueError("Row does not fit its container.")
        y = Constraints(1, height, Anchor.LEFT, vertical).resolve(self.content).y
        x = self.content.x
        result: list[Rect] = []
        for width in widths:
            result.append(Rect(x, y, width, height))
            x += width + self.gap
        return tuple(result)

    def column(self, heights: list[int], width: int, horizontal: Anchor = Anchor.CENTER_X) -> tuple[Rect, ...]:
        """Lay out heights from top to bottom with configured gaps."""
        required = sum(heights) + self.gap * max(0, len(heights) - 1)
        if required > self.content.height or width > self.content.width:
            raise ValueError("Column does not fit its container.")
        x = Constraints(width, 1, horizontal, Anchor.TOP).resolve(self.content).x
        y = self.content.y
        result: list[Rect] = []
        for height in heights:
            result.append(Rect(x, y, width, height))
            y += height + self.gap
        return tuple(result)


def fit_aspect(source_width: int, source_height: int, bounds: Rect) -> Rect:
    """Fit an aspect ratio inside bounds without cropping or distortion."""
    if source_width <= 0 or source_height <= 0:
        raise ValueError("Source dimensions must be positive.")
    scale = min(bounds.width / source_width, bounds.height / source_height)
    width, height = round(source_width * scale), round(source_height * scale)
    return Constraints(width, height).resolve(bounds)


def safe_area(name: str, canvas: Rect) -> Rect:
    """Return a named safe area scaled from the target canvas dimensions."""
    if name == "youtube_critical":
        width, height = 1546, 423
        return Rect((canvas.width - width) // 2, (canvas.height - height) // 2, width, height)
    if name in {"twitch", "obs"}:
        return canvas.inset(round(min(canvas.width, canvas.height) * 0.05))
    if name in {"social", "discord", "twitter", "bluesky"}:
        return canvas.inset(round(min(canvas.width, canvas.height) * 0.08))
    raise ValueError(f"Unknown safe area: {name}")
