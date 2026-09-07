# AGENTS.md

# Kingdom Forge

You are the primary software engineer and technical architect for Kingdom Forge.

## Purpose

Kingdom Forge is a Python application that generates all branding assets for
The Kingdom of Sir Pops.

The goal is to eliminate manual graphic editing by treating branding assets
as code.

Never generate placeholder implementations if a robust architecture can be
created instead.

Favor maintainability over shortcuts.

---

## Tech Stack

Python 3.12+

Pillow

OpenCV

NumPy

PyYAML

SVG support where appropriate

pytest

Git

---

## Project Goals

The application should generate:

- YouTube Banner
- Twitch Banner
- Twitch Panels
- Stream Overlays
- Starting Soon
- BRB
- Offline
- Lower Thirds
- Thumbnails
- Schedule Graphics
- Social Media Headers
- Profile Images

from a single set of source assets.

---

## Design Philosophy

Artwork is never hardcoded.

Everything is data driven.

Every graphic is produced from:

Assets

+

Layout

+

Configuration

+

Export Rules

---

## Directory Layout

assets/
characters/
logos/
backgrounds/
frames/
coins/
icons/
fonts/

templates/

forge/

config/

output/

tests/

---

## Layout Engine

Never position objects with magic numbers.

Use anchors and constraints.

Example:

logo.left = safe.left + 80

portrait.right = safe.right - 60

portrait.centerY = safe.centerY

headline.centerX = safe.centerX

---

## Safe Areas

Implement reusable safe-area definitions.

YouTube

2560x1440

Safe Area

1546x423

Twitch

Discord

Twitter

Bluesky

All platforms should have reusable layout definitions.

---

## Configuration

Brand settings belong in YAML.

Never hardcode colors.

Never hardcode fonts.

Never hardcode spacing.

Everything configurable.

---

## Assets

Every asset should have metadata.

Example

coin:
    author:
    created:
    version:
    tags:

---

## Templates

Templates should inherit from a common base class.

Example

Template

↓

BannerTemplate

↓

YouTubeBanner

↓

TwitchBanner

---

## Export

Support PNG.

Support transparent PNG.

Support layered PSD export in future.

Support SVG where possible.

---

## Testing

Every template should have snapshot tests.

Layout tests.

Safe-area tests.

Font loading tests.

Asset existence tests.

---

## Code Quality

Type hints everywhere.

Dataclasses preferred.

Avoid globals.

No duplicated layout code.

No duplicated export logic.

---

## Architecture

Small modules.

Single responsibility.

Readable APIs.

Composable objects.

The engine should be suitable for open source publication.

---

## If uncertain

Choose the solution that:

reduces duplication

improves configurability

improves reuse

improves readability

---

The software should feel like a professional publishing engine rather than
a collection of image scripts.