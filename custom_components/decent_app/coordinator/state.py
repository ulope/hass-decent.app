"""
Coordinator state container for decent_app.

Holds the merged view of REST-polled and WebSocket-pushed data from the
Decent.app gateway. Entities read from this object exclusively via
coordinator.data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from custom_components.decent_app.utils import camel_to_snake


@dataclass
class DecentAppState:
    """
    Snapshot of all gateway data exposed to entities.

    WebSocket channels update individual fields as frames arrive; the REST
    fallback poll refreshes device/profile/workflow information. A new
    (shallow-copied) instance is pushed to the coordinator on every update
    so that unchanged data can be de-duplicated by the coordinator.
    """

    app_info: dict[str, Any] = field(default_factory=dict)
    machine_info: dict[str, Any] = field(default_factory=dict)
    devices: list[dict[str, Any]] = field(default_factory=list)
    machine_snapshot: dict[str, Any] = field(default_factory=dict)
    water_levels: dict[str, Any] = field(default_factory=dict)
    shot_settings: dict[str, Any] = field(default_factory=dict)
    scale_snapshot: dict[str, Any] = field(default_factory=dict)
    scale_connected: bool = False
    workflow: dict[str, Any] = field(default_factory=dict)
    profiles: list[dict[str, Any]] = field(default_factory=list)

    @property
    def machine_connected(self) -> bool:
        """Return True if a machine is currently connected to the gateway."""
        return any(device.get("type") == "machine" and device.get("state") == "connected" for device in self.devices)

    @property
    def machine_state(self) -> str | None:
        """Return the current machine state name (snake_case), if known."""
        state = self.machine_snapshot.get("state")
        if isinstance(state, dict) and state.get("state"):
            return camel_to_snake(state["state"])
        return None

    @property
    def machine_substate(self) -> str | None:
        """Return the current machine substate name (snake_case), if known."""
        state = self.machine_snapshot.get("state")
        if isinstance(state, dict) and state.get("substate"):
            return camel_to_snake(state["substate"])
        return None
