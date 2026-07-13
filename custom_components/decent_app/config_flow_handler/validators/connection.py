"""Connection validation for the decent_app config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.decent_app.api import DecentAppApiClient, DecentAppApiClientError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def validate_connection(hass: HomeAssistant, host: str, port: int) -> dict[str, Any]:
    """
    Verify that a Decent.app gateway is reachable at host:port.

    Returns:
        A dict with the gateway build info ("app_info") and, when a
        machine is currently connected, its serial number ("serial").

    Raises:
        DecentAppApiClientCommunicationError: If the gateway is unreachable.
        DecentAppApiClientError: For unexpected API errors.

    """
    client = DecentAppApiClient(host=host, port=port, session=async_get_clientsession(hass))
    app_info = await client.async_get_app_info()

    serial: str | None = None
    try:
        machine_info = await client.async_get_machine_info()
        serial = machine_info.get("serialNumber") or None
    except DecentAppApiClientError:
        # No machine connected right now - that is fine for setup.
        serial = None

    return {"app_info": app_info, "serial": serial}
