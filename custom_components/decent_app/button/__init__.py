"""Button platform for decent_app."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.decent_app.const import PARALLEL_UPDATES as PARALLEL_UPDATES

from .machine_actions import ENTITY_DESCRIPTIONS as MACHINE_DESCRIPTIONS, DecentAppMachineButton
from .scale_actions import ENTITY_DESCRIPTIONS as SCALE_DESCRIPTIONS, DecentAppScaleButton

if TYPE_CHECKING:
    from custom_components.decent_app.data import DecentAppConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DecentAppConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator = entry.runtime_data.coordinator
    entities: list[DecentAppMachineButton | DecentAppScaleButton] = [
        DecentAppMachineButton(coordinator=coordinator, entity_description=entity_description)
        for entity_description in MACHINE_DESCRIPTIONS
    ]
    entities.extend(
        DecentAppScaleButton(coordinator=coordinator, entity_description=entity_description)
        for entity_description in SCALE_DESCRIPTIONS
    )
    async_add_entities(entities)
