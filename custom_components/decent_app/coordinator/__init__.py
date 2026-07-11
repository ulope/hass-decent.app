"""
Data update coordinator package for decent_app.

Package structure:
- base.py: Main coordinator class (DecentAppDataUpdateCoordinator)
- commands.py: Write operations exposed to entities and service actions
- state.py: The DecentAppState container distributed to entities
"""

from __future__ import annotations

from .base import DecentAppDataUpdateCoordinator
from .state import DecentAppState

__all__ = ["DecentAppDataUpdateCoordinator", "DecentAppState"]
