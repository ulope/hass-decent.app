"""Number platform for decent_app."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.decent_app.const import PARALLEL_UPDATES as PARALLEL_UPDATES

from .shot_settings import ENTITY_DESCRIPTIONS as SHOT_SETTING_DESCRIPTIONS, DecentAppShotSettingNumber
from .water import ENTITY_DESCRIPTIONS as WATER_DESCRIPTIONS, DecentAppWaterRefillNumber

if TYPE_CHECKING:
    from custom_components.decent_app.data import DecentAppConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DecentAppConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator = entry.runtime_data.coordinator
    entities: list[DecentAppShotSettingNumber | DecentAppWaterRefillNumber] = [
        DecentAppShotSettingNumber(coordinator=coordinator, entity_description=entity_description)
        for entity_description in SHOT_SETTING_DESCRIPTIONS
    ]
    entities.extend(
        DecentAppWaterRefillNumber(coordinator=coordinator, entity_description=entity_description)
        for entity_description in WATER_DESCRIPTIONS
    )
    async_add_entities(entities)
