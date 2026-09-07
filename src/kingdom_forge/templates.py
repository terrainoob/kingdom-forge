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
        return Canvas(self.settings.width, self.settings.height, rgba if not self.settings.transparent else (*rgba[:3], 0))

    def _content_area(self) -> Rect:
        canvas = Rect(0, 0, self.settings.width, self.settings.height)
        return safe_area(self.settings.safe_area, canvas) if self.settings.safe_area else canvas.inset(self.context.brand.spacing["md"])

    def _paint_common_text(self, canvas: Canvas) -> None:
        area = self._content_area()
        text = TextPainter(self.context.fonts)
        display = self.context.brand.typography["display"]
        body = self.context.brand.typography["body"]
        text.centered(canvas, self.settings.headline, area, display, max(24, area.height // 7), parse_color(self.context.brand.palette["parchment"]), -self.context.brand.spacing["sm"])
        text.centered(canvas, self.settings.subtitle, area, body, max(18, area.height // 14), parse_color(self.context.brand.palette["gold"]), self.context.brand.spacing["sm"])
        text.centered(canvas, self.settings.tagline, area, body, max(14, area.height // 20), parse_color(self.context.brand.palette["parchment"]), self.context.brand.spacing["lg"])
        if self.context.guides:
            from PIL import ImageDraw
            ImageDraw.Draw(canvas.image).rectangle((area.x, area.y, area.right, area.bottom), outline=parse_color(self.context.brand.palette["gold"]), width=max(1, self.context.brand.spacing["xs"] // 8))

    def _paint_assets(self, canvas: Canvas) -> None:
        area = self._content_area()
        if self.settings.character:
            portrait = self.context.assets.image(self.settings.character)
            portrait_box = Constraints(area.width // 3, area.height, horizontal="right", vertical="bottom").resolve(area)
            target = fit_aspect(*portrait.size, portrait_box)
            canvas.paste(portrait, target)
        if self.settings.logo:
            logo = self.context.assets.image(self.settings.logo)
            logo_box = Constraints(area.width // 4, area.height // 4, horizontal="left", vertical="top").resolve(area)
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
