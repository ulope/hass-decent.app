"""Connectivity and status binary sensors for decent_app."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.decent_app.entity import DecentAppEntity
from custom_components.decent_app.entity_utils import build_scale_device_info
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_components.decent_app.coordinator import DecentAppDataUpdateCoordinator, DecentAppState


@dataclass(frozen=True, kw_only=True)
class DecentAppBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a binary sensor with its value extraction function."""

    value_fn: Callable[[DecentAppState], bool | None]
    require_machine: bool = True
    scale_device: bool = False


def _water_level_low(state: DecentAppState) -> bool | None:
    """Return True when the tank level dropped to the refill threshold."""
    current = state.water_levels.get("currentLevel")
    refill = state.water_levels.get("refillLevel")
    if current is None or refill is None:
        return None
    return current <= refill


ENTITY_DESCRIPTIONS: tuple[DecentAppBinarySensorEntityDescription, ...] = (
    DecentAppBinarySensorEntityDescription(
        key="machine_connected",
        translation_key="machine_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.machine_connected,
        require_machine=False,
    ),
    DecentAppBinarySensorEntityDescription(
        key="scale_connected",
        translation_key="scale_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.scale_connected,
        require_machine=False,
        scale_device=True,
    ),
    DecentAppBinarySensorEntityDescription(
        key="water_level_low",
        translation_key="water_level_low",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=_water_level_low,
    ),
)


class DecentAppBinarySensor(BinarySensorEntity, DecentAppEntity):
    """Binary sensor reading a boolean from the coordinator data."""

    entity_description: DecentAppBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: DecentAppDataUpdateCoordinator,
        entity_description: DecentAppBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entity_description)
        self._require_machine = entity_description.require_machine
        if entity_description.scale_device:
            self._attr_device_info = build_scale_device_info(coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return the current state."""
        return self.entity_description.value_fn(self.coordinator.data)
