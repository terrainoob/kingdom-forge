"""Tests for rendering, export, and publishing."""

from pathlib import Path

from PIL import Image

from kingdom_forge.config import load_project_config
from kingdom_forge.publishing import Publisher


def test_publisher_outputs_png_and_manifest(project_yaml: Path, tmp_path: Path) -> None:
    report = Publisher(load_project_config(project_yaml)).build(guides=True)
    image_path = tmp_path / "output" / "banner.png"
    assert len(report.artifacts) == 1
    assert (tmp_path / "output" / "manifest.json").is_file()
    with Image.open(image_path) as image:
        assert image.mode == "RGBA"
        assert image.size == (640, 360)


def test_publisher_reuses_unchanged_artifact(project_yaml: Path) -> None:
    publisher = Publisher(load_project_config(project_yaml))
    publisher.build()
    report = publisher.build()
    assert report.artifacts[0].reused is True
