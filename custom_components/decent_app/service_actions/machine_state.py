"""Handler for the set_machine_state service action."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.decent_app.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ServiceValidationError

if TYPE_CHECKING:
    from custom_components.decent_app.data import DecentAppConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall


def _resolve_entry(hass: HomeAssistant, call: ServiceCall) -> DecentAppConfigEntry:
    """Resolve the target config entry for a service call."""
    entry_id = call.data.get("config_entry_id")
    entries = [entry for entry in hass.config_entries.async_entries(DOMAIN) if entry.state is ConfigEntryState.LOADED]
    if entry_id:
        entry = next((entry for entry in entries if entry.entry_id == entry_id), None)
        if entry is None:
            msg = f"No loaded Decent.app config entry with id {entry_id}"
            raise ServiceValidationError(msg)
        return entry
    if not entries:
        msg = "No loaded Decent.app config entries"
        raise ServiceValidationError(msg)
    return entries[0]


async def async_handle_set_machine_state(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle the set_machine_state service action."""
    entry = _resolve_entry(hass, call)
    await entry.runtime_data.coordinator.async_set_machine_state(call.data["state"])
