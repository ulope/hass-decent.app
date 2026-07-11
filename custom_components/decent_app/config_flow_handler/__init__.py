"""
Config flow handler package for decent_app.

Package structure:
------------------
- config_flow.py: Main configuration flow (user setup, reconfigure)
- schemas/: Voluptuous schemas for the forms
- validators/: Connection validation logic

Usage:
------
The main config flow handler is imported in config_flow.py at the integration root:

    from .config_flow_handler import DecentAppConfigFlowHandler
"""

from __future__ import annotations

from .config_flow import DecentAppConfigFlowHandler

__all__ = ["DecentAppConfigFlowHandler"]
