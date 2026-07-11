"""
Config flow for decent_app.

The Decent.app gateway requires no authentication; setup only needs the
host (tablet IP or hostname) and port of the gateway. When a machine is
connected during setup its serial number is used as the unique ID.
"""

from __future__ import annotations

from typing import Any

from custom_components.decent_app.api import DecentAppApiClientCommunicationError
from custom_components.decent_app.config_flow_handler.schemas import get_user_schema
from custom_components.decent_app.config_flow_handler.validators import validate_connection
from custom_components.decent_app.const import CONF_HOST, CONF_PORT, DEFAULT_PORT, DOMAIN, LOGGER
from homeassistant import config_entries


class DecentAppConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Handle the config flow for a Decent.app gateway.

    Supported flows:
    - user: Initial setup via UI (host + port)
    - reconfigure: Update the gateway address
    """

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            data = self._normalize_input(user_input)
            try:
                result = await validate_connection(
                    self.hass,
                    host=data[CONF_HOST],
                    port=data[CONF_PORT],
                )
            except DecentAppApiClientCommunicationError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unexpected error validating Decent.app gateway")
                errors["base"] = "unknown"
            else:
                if result["serial"]:
                    await self.async_set_unique_id(result["serial"])
                    self._abort_if_unique_id_configured(updates=data)
                else:
                    self._async_abort_entries_match({CONF_HOST: data[CONF_HOST]})

                return self.async_create_entry(
                    title=f"Decent Espresso ({data[CONF_HOST]})",
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=get_user_schema(user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle reconfiguration of the gateway address."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            data = self._normalize_input(user_input)
            try:
                await validate_connection(
                    self.hass,
                    host=data[CONF_HOST],
                    port=data[CONF_PORT],
                )
            except DecentAppApiClientCommunicationError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unexpected error validating Decent.app gateway")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(entry, data=data)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=get_user_schema(user_input or entry.data),
            errors=errors,
        )

    @staticmethod
    def _normalize_input(user_input: dict[str, Any]) -> dict[str, Any]:
        """Normalize form input (strip host, coerce port to int)."""
        return {
            CONF_HOST: str(user_input[CONF_HOST]).strip(),
            CONF_PORT: int(user_input.get(CONF_PORT, DEFAULT_PORT)),
        }


__all__ = ["DecentAppConfigFlowHandler"]
