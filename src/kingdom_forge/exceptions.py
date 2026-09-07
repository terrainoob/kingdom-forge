"""Domain-specific errors raised by Kingdom Forge."""


class KingdomForgeError(Exception):
    """Base class for expected Kingdom Forge failures."""


class ConfigurationError(KingdomForgeError):
    """Raised when a project configuration is missing or invalid."""

