"""Reusable template hierarchy for platform graphics."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from kingdom_forge.assets import AssetManager
from kingdom_forge.config import BrandSettings, TemplateSettings
from kingdom_forge.layout import Constraints, Rect, fit_aspect, safe_area
from kingdom_forge.render import Canvas, FontLoader, TextPainter, parse_color


@dataclass(slots=True)
class TemplateContext:
    """Shared, dependency-injected services available to a template."""
    brand: BrandSettings
    assets: AssetManager
    fonts: FontLoader
    guides: bool = False


class Template(ABC):
    """Base contract for all Kingdom Forge graphics."""
    def __init__(self, settings: TemplateSettings, context: TemplateContext) -> None:
        self.settings = settings
        self.context = context

    @abstractmethod
    def render(self) -> Canvas:
        """Render this template to a canvas."""

    def _canvas(self) -> Canvas:
        color = self.context.brand.palette.get(self.settings.background_color, self.settings.background_color)
        rgba = parse_color(color)
        canvas = Canvas(self.settings.width, self.settings.height, rgba if not self.settings.transparent else (*rgba[:3], 0))
        if self.settings.background_image:
            canvas.cover(self.context.assets.image(self.settings.background_image), self.settings.background_opacity)
        return canvas

    def _content_area(self) -> Rect:
        canvas = Rect(0, 0, self.settings.width, self.settings.height)
        return safe_area(self.settings.safe_area, canvas) if self.settings.safe_area else canvas.inset(self.context.brand.spacing["md"])

    def _paint_common_text(self, canvas: Canvas) -> None:
        area = self._content_area()
        copy_area = self._copy_area(area)
        text = TextPainter(self.context.fonts)
        display = self.context.brand.typography["display"]
        body = self.context.brand.typography["body"]
        if self.settings.copy_layout == "stacked":
            self._paint_stacked_copy(canvas, text, copy_area, display, body)
        else:
            self._paint_legacy_copy(canvas, text, area, copy_area, display, body)
        if self.context.guides:
            from PIL import ImageDraw
            ImageDraw.Draw(canvas.image).rectangle((area.x, area.y, area.right, area.bottom), outline=parse_color(self.context.brand.palette["gold"]), width=max(1, self.context.brand.spacing["xs"] // 8))

    def _paint_legacy_copy(self, canvas: Canvas, text: TextPainter, area: Rect, copy_area: Rect, display: str, body: str) -> None:
        copy_offset = self.settings.copy_offset_y
        text.centered(canvas, self.settings.headline, copy_area, display, max(24, area.height // 7), parse_color(self.context.brand.palette["parchment"]), -self.context.brand.spacing["sm"] + copy_offset)
        text.centered(canvas, self.settings.subtitle, copy_area, body, max(18, area.height // 14), parse_color(self.context.brand.palette["gold"]), self.context.brand.spacing["sm"] + copy_offset)
        text.centered(canvas, self.settings.tagline, copy_area, body, max(14, area.height // 20), parse_color(self.context.brand.palette["parchment"]), self.context.brand.spacing["lg"] + copy_offset)

    def _paint_stacked_copy(self, canvas: Canvas, text: TextPainter, area: Rect, display: str, body: str) -> None:
        lines = [
            (self.settings.headline, display, max(24, area.height // 7), parse_color(self.context.brand.palette["parchment"])),
            (self.settings.subtitle, body, max(18, area.height // 14), parse_color(self.context.brand.palette["gold"])),
            (self.settings.tagline, body, max(14, area.height // 20), parse_color(self.context.brand.palette["parchment"])),
        ]
        visible = [line for line in lines if line[0]]
        if not visible:
            return
        gap = self.context.brand.spacing["xs"]
        total_height = sum(size for _, _, size, _ in visible) + gap * (len(visible) - 1)
        y = area.center[1] + self.settings.copy_offset_y - total_height // 2
        for content, font, size, color in visible:
            text.centered(canvas, content, area, font, size, color, y - area.center[1])
            y += size + gap

    def _copy_area(self, area: Rect) -> Rect:
        if self.settings.copy_anchor == "full":
            return area
        return Constraints(round(area.width * self.settings.copy_width), area.height, horizontal="left", vertical="center_y").resolve(area)

    def _paint_assets(self, canvas: Canvas) -> None:
        area = self._content_area()
        if self.settings.character:
            portrait = self.context.assets.image(self.settings.character)
            portrait_box = Constraints(area.width // 3, area.height, horizontal="right", vertical="bottom").resolve(area)
            target = fit_aspect(*portrait.size, portrait_box)
            canvas.paste(portrait, target)
        if self.settings.logo:
            logo = self.context.assets.image(self.settings.logo)
            anchors = {"top_left": ("left", "top"), "top_center": ("center_x", "top"), "center": ("center_x", "center_y")}
            horizontal, vertical = anchors[self.settings.logo_anchor]
            logo_box = Constraints(round(area.width * self.settings.logo_scale), round(area.height * self.settings.logo_scale), horizontal=horizontal, vertical=vertical).resolve(area)
            target = fit_aspect(*logo.size, logo_box)
            canvas.paste(logo, target)


class BannerTemplate(Template):
    """Common banner implementation used by YouTube and Twitch variants."""
    def render(self) -> Canvas:
        """Render background, optional assets, and aligned campaign copy."""
        canvas = self._canvas()
        self._paint_assets(canvas)
        self._paint_common_text(canvas)
        return canvas


class YouTubeBanner(BannerTemplate):
    """YouTube banner template with the critical-viewing safe area."""


class TwitchBanner(BannerTemplate):
    """Twitch banner template."""


class PanelTemplate(BannerTemplate):
    """Twitch panel template."""


class ThumbnailTemplate(BannerTemplate):
    """Episode or game thumbnail template."""


class OverlayTemplate(BannerTemplate):
    """Stream overlay, lower-third, and scene template."""


def template_for(settings: TemplateSettings, context: TemplateContext) -> Template:
    """Select the appropriate template class for a configured template kind."""
    kinds: dict[str, type[Template]] = {
        "youtube_banner": YouTubeBanner, "twitch_banner": TwitchBanner, "panel": PanelTemplate,
        "thumbnail": ThumbnailTemplate, "overlay": OverlayTemplate,
        "twitch_starting_soon": OverlayTemplate, "twitch_brb": OverlayTemplate,
        "twitch_offline": OverlayTemplate, "schedule": OverlayTemplate, "lower_third": OverlayTemplate,
        "social_header": BannerTemplate, "profile_image": ThumbnailTemplate,
    }
    try:
        return kinds[settings.kind](settings, context)
    except KeyError as error:
        raise ValueError(f"Unsupported template kind: {settings.kind}") from error
