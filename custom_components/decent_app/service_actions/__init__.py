"""Service actions package for decent_app."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol

from custom_components.decent_app.const import DOMAIN, REQUESTABLE_MACHINE_STATES
import homeassistant.helpers.config_validation as cv

from .machine_state import async_handle_set_machine_state

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

# Service action names - only used within the service_actions module
SERVICE_SET_MACHINE_STATE = "set_machine_state"

SET_MACHINE_STATE_SCHEMA = vol.Schema(
    {
        vol.Required("state"): vol.In(REQUESTABLE_MACHINE_STATES),
        vol.Optional("config_entry_id"): cv.string,
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """
    Register services for the integration.

    Services are registered at component level (in async_setup) rather than
    per config entry - a Silver Quality Scale requirement.
    """

    async def handle_set_machine_state(call: ServiceCall) -> None:
        """Handle the set_machine_state service call."""
        await async_handle_set_machine_state(hass, call)

    if not hass.services.has_service(DOMAIN, SERVICE_SET_MACHINE_STATE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_MACHINE_STATE,
            handle_set_machine_state,
            schema=SET_MACHINE_STATE_SCHEMA,
        )
