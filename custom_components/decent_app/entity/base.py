"""
Base entity classes for decent_app.

All entities inherit from DecentAppEntity (machine device) or
DecentAppScaleEntity (scale device). Both read data exclusively from
coordinator.data and issue commands through the coordinator.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.decent_app.const import ATTRIBUTION
from custom_components.decent_app.coordinator import DecentAppDataUpdateCoordinator
from custom_components.decent_app.entity_utils import build_machine_device_info, build_scale_device_info
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class DecentAppEntity(CoordinatorEntity[DecentAppDataUpdateCoordinator]):
    """
    Base entity for the espresso machine device.

    Provides coordinator wiring, unique ID generation
    ({entry_id}_{description.key}), device info and availability based on
    the gateway being reachable and the machine being connected.

    Set _require_machine = False on subclasses or instances that should
    stay available while no machine is connected to the gateway (e.g. the
    machine connectivity binary sensor).
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _require_machine = True

    def __init__(
        self,
        coordinator: DecentAppDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """
        Initialize the base entity.

        Args:
            coordinator: The data update coordinator for this entity.
            entity_description: The entity description defining characteristics.

        """
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = build_machine_device_info(coordinator)

    @property
    def available(self) -> bool:
        """Available when the gateway is reachable (and the machine connected)."""
        if not super().available:
            return False
        return not self._require_machine or self.coordinator.data.machine_connected


class DecentAppScaleEntity(DecentAppEntity):
    """Base entity for the scale device."""

    _require_machine = False

    def __init__(
        self,
        coordinator: DecentAppDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the scale entity."""
        super().__init__(coordinator, entity_description)
        self._attr_device_info = build_scale_device_info(coordinator)

    @property
    def available(self) -> bool:
        """Available when the gateway is reachable and a scale is connected."""
        if not super().available:
            return False
        return self.coordinator.data.scale_connected
