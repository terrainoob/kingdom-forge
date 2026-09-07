"""Incremental batch publishing, manifests, and build reporting."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path

from kingdom_forge.assets import AssetManager
from kingdom_forge.config import ProjectConfig
from kingdom_forge.render import FontLoader, PngExporter
from kingdom_forge.templates import TemplateContext, template_for


@dataclass(frozen=True, slots=True)
class BuildArtifact:
    """One output included in a build manifest."""
    template: str
    path: str
    digest: str
    input_digest: str
    reused: bool


@dataclass(frozen=True, slots=True)
class BuildReport:
    """Serializable summary of a publishing operation."""
    version: str
    artifacts: tuple[BuildArtifact, ...]


class Publisher:
    """Build configured templates and write a reproducible output manifest."""
    def __init__(self, config: ProjectConfig) -> None:
        self._config = config
        self._assets = AssetManager(config.project.assets_directory)
        self._exporter = PngExporter()

    def build(self, names: set[str] | None = None, guides: bool = False) -> BuildReport:
        """Render selected templates, reusing outputs with identical inputs."""
        artifacts: list[BuildArtifact] = []
        context = TemplateContext(self._config.brand, self._assets, FontLoader(), guides)
        previous = self._previous_inputs()
        for settings in self._config.templates:
            if names is not None and settings.name not in names:
                continue
            destination = self._config.project.output_directory / f"{settings.output_name or settings.name}.png"
            input_digest = self._input_digest(settings.name, guides)
            reusable = destination.is_file() and previous.get(settings.name) == input_digest
            if not reusable:
                canvas = template_for(settings, context).render()
                self._exporter.export(canvas, destination)
            artifacts.append(BuildArtifact(settings.name, str(destination), _digest(destination), input_digest, reusable))
        report = BuildReport(self._config.project.version, tuple(artifacts))
        self._write_manifest(report)
        return report

    def validate(self) -> None:
        """Validate all configured external asset references before publication."""
        for template in self._config.templates:
            for asset in (template.logo, template.character):
                if asset:
                    self._assets.resolve(asset)

    def _write_manifest(self, report: BuildReport) -> None:
        output = self._config.project.output_directory
        output.mkdir(parents=True, exist_ok=True)
        (output / "manifest.json").write_text(json.dumps(asdict(report), indent=2, sort_keys=True), encoding="utf-8")
        lines = [f"Kingdom Forge build {report.version}", f"Artifacts: {len(report.artifacts)}"]
        lines.extend(f"- {artifact.template}: {artifact.path}" for artifact in report.artifacts)
        (output / "build-report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _previous_inputs(self) -> dict[str, str]:
        """Read recorded input digests from the previous manifest, if any."""
        manifest = self._config.project.output_directory / "manifest.json"
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            return {item["template"]: item["input_digest"] for item in data.get("artifacts", [])}
        except (OSError, ValueError, KeyError, TypeError):
            return {}

    def _input_digest(self, template_name: str, guides: bool) -> str:
        """Hash the complete build input that can change a template's pixels."""
        digest = sha256()
        digest.update(self._config.source_path.read_bytes())
        digest.update(template_name.encode())
        digest.update(str(guides).encode())
        for asset in self._assets.inventory():
            digest.update(str(asset.path).encode())
            digest.update(asset.digest.encode())
        return digest.hexdigest()


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()
