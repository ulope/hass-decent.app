"""
Command helpers for the decent_app coordinator.

Entities never call the API client directly (Entities → Coordinator → API
Client); this mixin exposes all write operations on the coordinator and
applies optimistic state updates where the gateway does not push a
confirmation frame immediately.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from custom_components.decent_app.api import DecentAppApiClientError
from homeassistant.exceptions import HomeAssistantError

if TYPE_CHECKING:
    from custom_components.decent_app.api import DecentAppApiClient

    from .state import DecentAppState


class _CommandsHost(Protocol):
    """Attributes the mixin expects from the coordinator."""

    client: DecentAppApiClient

    @property
    def state(self) -> DecentAppState: ...

    def push_state(self) -> None: ...


class DecentAppCommandsMixin:
    """Write operations exposed to entities and service actions."""

    async def async_set_machine_state(self: _CommandsHost, state: str) -> None:
        """
        Request a machine state change (idle, sleeping, espresso, ...).

        The resulting state is reported back via the machine snapshot
        WebSocket channel, so no optimistic update is needed.
        """
        try:
            await self.client.async_set_machine_state(state)
        except DecentAppApiClientError as exception:
            msg = f"Failed to set machine state to {state}: {exception}"
            raise HomeAssistantError(msg) from exception

    async def async_tare_scale(self: _CommandsHost) -> None:
        """Tare the connected scale."""
        try:
            await self.client.async_tare_scale()
        except DecentAppApiClientError as exception:
            msg = f"Failed to tare scale: {exception}"
            raise HomeAssistantError(msg) from exception

    async def async_set_shot_setting(self: _CommandsHost, key: str, value: float) -> None:
        """
        Update a single shot setting field.

        The gateway expects the full ShotSettings object, so the current
        settings (received via WebSocket) are used as the base.
        """
        settings: dict[str, Any] = dict(self.state.shot_settings)
        if not settings:
            msg = "Shot settings not yet received from the gateway; cannot update"
            raise HomeAssistantError(msg)
        # All ShotSettings fields are integers except groupTemp
        settings[key] = value if key == "groupTemp" else int(round(value))
        try:
            await self.client.async_set_shot_settings(settings)
        except DecentAppApiClientError as exception:
            msg = f"Failed to update shot setting {key}: {exception}"
            raise HomeAssistantError(msg) from exception
        self.state.shot_settings = settings
        self.push_state()

    async def async_set_water_refill_level(self: _CommandsHost, refill_level: float) -> None:
        """Set the water tank refill warning threshold in mm."""
        try:
            await self.client.async_set_water_refill_level(refill_level)
        except DecentAppApiClientError as exception:
            msg = f"Failed to set water refill level: {exception}"
            raise HomeAssistantError(msg) from exception
        self.state.water_levels = {**self.state.water_levels, "refillLevel": refill_level}
        self.push_state()

    async def async_select_profile(self: _CommandsHost, profile_id: str) -> None:
        """
        Apply a stored profile to the current workflow.

        Updating the workflow uploads the profile to the machine as one
        atomic operation (recommended over POST /machine/profile).
        """
        record = next(
            (record for record in self.state.profiles if record.get("id") == profile_id),
            None,
        )
        if record is None or not record.get("profile"):
            msg = f"Unknown profile: {profile_id}"
            raise HomeAssistantError(msg)
        try:
            workflow = await self.client.async_update_workflow({"profile": record["profile"]})
        except DecentAppApiClientError as exception:
            msg = f"Failed to apply profile {profile_id}: {exception}"
            raise HomeAssistantError(msg) from exception
        if isinstance(workflow, dict) and workflow:
            self.state.workflow = workflow
        else:
            self.state.workflow = {**self.state.workflow, "profile": record["profile"]}
        self.push_state()
