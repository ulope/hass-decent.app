"""Machine telemetry sensors for decent_app.

Values come from the machine snapshot and water level WebSocket channels
(ws/v1/machine/snapshot, ws/v1/machine/waterLevels).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.decent_app.const import MACHINE_STATES, MACHINE_SUBSTATES
from custom_components.decent_app.entity import DecentAppEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import EntityCategory, UnitOfPressure, UnitOfTemperature

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_components.decent_app.coordinator import DecentAppState
    from homeassistant.helpers.typing import StateType


@dataclass(frozen=True, kw_only=True)
class DecentAppMachineSensorEntityDescription(SensorEntityDescription):
    """Describes a machine sensor with its value extraction function."""

    value_fn: Callable[[DecentAppState], StateType]


def _snapshot_value(key: str) -> Callable[[DecentAppState], StateType]:
    """Build a value function reading a numeric field from the machine snapshot."""

    def _value(state: DecentAppState) -> StateType:
        return state.machine_snapshot.get(key)

    return _value


ENTITY_DESCRIPTIONS: tuple[DecentAppMachineSensorEntityDescription, ...] = (
    DecentAppMachineSensorEntityDescription(
        key="machine_state",
        translation_key="machine_state",
        device_class=SensorDeviceClass.ENUM,
        options=MACHINE_STATES,
        value_fn=lambda state: state.machine_state,
    ),
    DecentAppMachineSensorEntityDescription(
        key="machine_substate",
        translation_key="machine_substate",
        device_class=SensorDeviceClass.ENUM,
        options=MACHINE_SUBSTATES,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.machine_substate,
    ),
    DecentAppMachineSensorEntityDescription(
        key="pressure",
        translation_key="pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=_snapshot_value("pressure"),
    ),
    DecentAppMachineSensorEntityDescription(
        key="flow",
        translation_key="flow",
        native_unit_of_measurement="mL/s",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=_snapshot_value("flow"),
    ),
    DecentAppMachineSensorEntityDescription(
        key="group_temperature",
        translation_key="group_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=_snapshot_value("groupTemperature"),
    ),
    DecentAppMachineSensorEntityDescription(
        key="mix_temperature",
        translation_key="mix_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=_snapshot_value("mixTemperature"),
    ),
    DecentAppMachineSensorEntityDescription(
        key="steam_temperature",
        translation_key="steam_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=_snapshot_value("steamTemperature"),
    ),
    DecentAppMachineSensorEntityDescription(
        key="target_pressure",
        translation_key="target_pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_snapshot_value("targetPressure"),
    ),
    DecentAppMachineSensorEntityDescription(
        key="target_flow",
        translation_key="target_flow",
        native_unit_of_measurement="mL/s",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_snapshot_value("targetFlow"),
    ),
    DecentAppMachineSensorEntityDescription(
        key="target_group_temperature",
        translation_key="target_group_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_snapshot_value("targetGroupTemperature"),
    ),
    DecentAppMachineSensorEntityDescription(
        key="target_mix_temperature",
        translation_key="target_mix_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_snapshot_value("targetMixTemperature"),
    ),
    DecentAppMachineSensorEntityDescription(
        key="water_level",
        translation_key="water_level",
        native_unit_of_measurement="mm",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda state: state.water_levels.get("currentLevel"),
    ),
    DecentAppMachineSensorEntityDescription(
        key="profile_frame",
        translation_key="profile_frame",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_snapshot_value("profileFrame"),
    ),
)


class DecentAppMachineSensor(SensorEntity, DecentAppEntity):
    """Sensor reading a value from the coordinator's machine data."""

    entity_description: DecentAppMachineSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the current value."""
        return self.entity_description.value_fn(self.coordinator.data)
