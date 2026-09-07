"""Tests for constraints and platform safe areas."""

from kingdom_forge.layout import Anchor, Constraints, Container, Rect, fit_aspect, safe_area


def test_constraints_resolve_against_container() -> None:
    result = Constraints(20, 10, Anchor.RIGHT, Anchor.BOTTOM, -5, -2).resolve(Rect(0, 0, 100, 50))
    assert result == Rect(75, 38, 20, 10)


def test_youtube_safe_area_is_centered() -> None:
    area = safe_area("youtube_critical", Rect(0, 0, 2560, 1440))
    assert area == Rect(507, 508, 1546, 423)


def test_container_and_aspect_fit_are_constraint_based() -> None:
    container = Container(Rect(0, 0, 100, 50), padding=5, gap=5)
    assert container.row([20, 20], 10) == (Rect(5, 20, 20, 10), Rect(30, 20, 20, 10))
    assert fit_aspect(16, 9, Rect(0, 0, 100, 100)) == Rect(0, 22, 100, 56)
