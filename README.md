# Kingdom Forge

Kingdom Forge is a configuration-driven publishing engine for generating The Kingdom of Sir Pops branding assets. It treats artwork as code: source assets, YAML configuration, constraint layouts, and export rules produce repeatable platform graphics.

## Requirements

- Python 3.12 or later

## Development setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Configuration and CLI

`config/project.yaml` is the single source of truth for project paths, semantic color tokens, font roles, spacing, and graphics to publish. Templates name colors and assets; they do not embed branding values in Python code.

```powershell
kingdom-forge validate
kingdom-forge show-config
kingdom-forge list
kingdom-forge build
kingdom-forge build --template youtube-banner --guides
kingdom-forge --config path\to\project.yaml validate
```

## Publishing workflow

`kingdom-forge build` renders every configured template as an optimized RGBA PNG. It also writes `output/manifest.json`, with version and SHA-256 digests, and `output/build-report.txt`. Use `--template` repeatedly for focused builds; use `--guides` to export previews with visible safe-area guides.

The template hierarchy supports YouTube and Twitch banners, panels, stream scenes (Starting Soon, BRB, Offline), overlays, lower thirds, schedules, and thumbnails. Add a YAML template entry with platform dimensions and copy, then use optional `logo` and `character` paths relative to `assets/`.

## Layout and assets

Layouts use rectangles, anchors, constraints, relative sizing, and named safe areas. The YouTube critical safe area is `1546 × 423` within a `2560 × 1440` banner; Twitch/OBS and social safe areas use reusable proportional insets.

Images are loaded as RGBA through an asset manager that blocks path traversal, caches decoded source files, and returns defensive copies. `AssetManager.inventory()` provides SHA-256 metadata for auditing source assets and finding duplicates.

## Tests

```powershell
python -m pytest
```
