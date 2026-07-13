"""Switch platform for decent_app."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.decent_app.const import PARALLEL_UPDATES as PARALLEL_UPDATES

from .power import ENTITY_DESCRIPTION as POWER_DESCRIPTION, DecentAppPowerSwitch

if TYPE_CHECKING:
    from custom_components.decent_app.data import DecentAppConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DecentAppConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        [
            DecentAppPowerSwitch(
                coordinator=entry.runtime_data.coordinator,
                entity_description=POWER_DESCRIPTION,
            )
        ]
    )
