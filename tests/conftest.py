"""Shared fixtures for Kingdom Forge tests."""

from pathlib import Path

import pytest


@pytest.fixture
def project_yaml(tmp_path: Path) -> Path:
    """Create a complete minimal project configuration."""
    path = tmp_path / "project.yaml"
    path.write_text("""project:\n  name: Test Kingdom\n  version: 1.2.3\n  output_directory: output\n  assets_directory: assets\nlogging:\n  level: INFO\nbrand:\n  palette:\n    night: \"#101827\"\n    parchment: \"#F7F1E3\"\n    gold: \"#E8BC55\"\n  typography:\n    display: DejaVuSans-Bold.ttf\n    body: DejaVuSans.ttf\n  spacing:\n    xs: 8\n    sm: 16\n    md: 32\n    lg: 64\n  corner_radius: 8\ntemplates:\n  - name: banner\n    kind: youtube_banner\n    width: 640\n    height: 360\n    background_color: night\n    headline: Test headline\n    safe_area: youtube_critical\n""", encoding="utf-8")
    return path
