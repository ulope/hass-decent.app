"""Scale sensors for decent_app.

Values come from the scale snapshot WebSocket channel (ws/v1/scale/snapshot),
which delivers smoothed weight, weight-derived flow and battery level.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.decent_app.entity import DecentAppScaleEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfMass

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_components.decent_app.coordinator import DecentAppState
    from homeassistant.helpers.typing import StateType


@dataclass(frozen=True, kw_only=True)
class DecentAppScaleSensorEntityDescription(SensorEntityDescription):
    """Describes a scale sensor with its value extraction function."""

    value_fn: Callable[[DecentAppState], StateType]


ENTITY_DESCRIPTIONS: tuple[DecentAppScaleSensorEntityDescription, ...] = (
    DecentAppScaleSensorEntityDescription(
        key="scale_weight",
        translation_key="scale_weight",
        native_unit_of_measurement=UnitOfMass.GRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda state: state.scale_snapshot.get("weight"),
    ),
    DecentAppScaleSensorEntityDescription(
        key="scale_flow",
        translation_key="scale_flow",
        native_unit_of_measurement="g/s",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda state: state.scale_snapshot.get("weightFlow"),
    ),
    DecentAppScaleSensorEntityDescription(
        key="scale_battery",
        translation_key="scale_battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.scale_snapshot.get("battery"),
    ),
)


class DecentAppScaleSensor(SensorEntity, DecentAppScaleEntity):
    """Sensor reading a value from the coordinator's scale data."""

    entity_description: DecentAppScaleSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the current value."""
        return self.entity_description.value_fn(self.coordinator.data)
