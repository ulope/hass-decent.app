"""Diagnostics support for decent_app.

Learn more about diagnostics:
https://developers.home-assistant.io/docs/core/integration_diagnostics
"""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.redact import async_redact_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import DecentAppConfigEntry

# The gateway API is unauthenticated; device identifiers (BLE MACs) and the
# machine serial number are still redacted as personally identifying data.
TO_REDACT = {
    "serialNumber",
    "id",
    "localIp",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: DecentAppConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator
    integration = entry.runtime_data.integration

    state = asdict(coordinator.data) if coordinator.data else {}
    # Profile records are large; keep only id/title/visibility
    state["profiles"] = [
        {
            "id": record.get("id"),
            "title": (record.get("profile") or {}).get("title"),
            "visibility": record.get("visibility"),
        }
        for record in state.get("profiles", [])
    ]

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "title": entry.title,
            "state": str(entry.state),
            "unique_id": "**REDACTED**" if entry.unique_id else None,
            "data": dict(entry.data),
        },
        "integration": {
            "name": integration.name,
            "version": integration.version,
            "domain": integration.domain,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
        },
        "state": async_redact_data(state, TO_REDACT),
    }
