# Kingdom Forge

Kingdom Forge is a configuration-driven publishing engine for generating The Kingdom of Sir Pops branding assets.

## Requirements

- Python 3.12 or later

## Development setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Configuration

Project configuration is YAML and is validated at load time. Start from `config/project.yaml`.

```powershell
kingdom-forge validate
kingdom-forge show-config
kingdom-forge --config path\to\project.yaml validate
```

## Tests

```powershell
python -m pytest
```

Rendering, brand definitions, and templates are introduced in later milestones. This initial release establishes their typed configuration and CLI boundary.

