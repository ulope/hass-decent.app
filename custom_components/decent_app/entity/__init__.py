"""
Entity package for decent_app.

Architecture:
    All platform entities inherit from (PlatformEntity, DecentAppEntity).
    MRO order matters — platform-specific class first, then the integration base.
    Entities read data from coordinator.data and NEVER call the API client directly.
    Unique IDs follow the pattern: {entry_id}_{description.key}

See entity/base.py for the base classes.
"""

from .base import DecentAppEntity, DecentAppScaleEntity

__all__ = ["DecentAppEntity", "DecentAppScaleEntity"]
