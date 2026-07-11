"""
Custom integration to integrate the Decent.app espresso gateway with Home Assistant.

Decent.app (ReaPrime) runs on the tablet attached to a Decent Espresso
machine and exposes a local REST + WebSocket API. This integration connects
to that gateway, streams live telemetry (machine state, pressure, flow,
temperatures, water level, scale weight) over WebSockets and exposes
controls for the machine (start/stop, sleep/wake, shot settings, brew
profile selection) and the connected scale (tare).

API documentation:
https://github.com/tadelv/reaprime/blob/main/assets/api/rest_v1.yml
https://github.com/tadelv/reaprime/blob/main/assets/api/websocket_v1.yml
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_loaded_integration

from .api import DecentAppApiClient, DecentAppWebsocketListener
from .const import CONF_HOST, CONF_PORT, DEFAULT_PORT, DOMAIN
from .coordinator import DecentAppDataUpdateCoordinator
from .data import DecentAppData
from .service_actions import async_setup_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import DecentAppConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

# This integration is configured via config entries only
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """
    Set up the integration.

    Called once at Home Assistant startup to register service actions.
    Registering here (instead of async_setup_entry) is a Silver Quality
    Scale requirement.
    """
    await async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DecentAppConfigEntry,
) -> bool:
    """
    Set up a Decent.app gateway from a config entry.

    Creates the REST client and WebSocket listener, wires them into the
    coordinator, performs the first refresh (which also starts the
    WebSocket subscriptions) and forwards setup to all platforms.
    """
    session = async_get_clientsession(hass)
    client = DecentAppApiClient(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        session=session,
    )
    websocket = DecentAppWebsocketListener(client.websocket_base_url, session)

    coordinator = DecentAppDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        client=client,
        websocket=websocket,
    )

    entry.runtime_data = DecentAppData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: DecentAppConfigEntry,
) -> bool:
    """Unload a config entry (the coordinator shuts down the WebSocket listener)."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.coordinator.async_shutdown()
    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: DecentAppConfigEntry,
) -> None:
    """Reload the config entry after configuration changes."""
    await hass.config_entries.async_reload(entry.entry_id)
