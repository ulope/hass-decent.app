"""Binary sensor platform for decent_app."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.decent_app.const import PARALLEL_UPDATES as PARALLEL_UPDATES

from .status import ENTITY_DESCRIPTIONS, DecentAppBinarySensor

if TYPE_CHECKING:
    from custom_components.decent_app.data import DecentAppConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DecentAppConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    async_add_entities(
        DecentAppBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )
