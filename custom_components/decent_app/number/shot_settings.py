"""Shot setting number entities for decent_app.

These map to the ShotSettings object of the gateway. Current values arrive
via the shot settings WebSocket channel; writes post the full (merged)
settings object back through the coordinator.
"""

from __future__ import annotations

from dataclasses import dataclass

from custom_components.decent_app.entity import DecentAppEntity
from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime, UnitOfVolume


@dataclass(frozen=True, kw_only=True)
class DecentAppShotSettingNumberEntityDescription(NumberEntityDescription):
    """Describes a number entity bound to a ShotSettings field."""

    settings_key: str


ENTITY_DESCRIPTIONS: tuple[DecentAppShotSettingNumberEntityDescription, ...] = (
    DecentAppShotSettingNumberEntityDescription(
        key="target_shot_volume",
        translation_key="target_shot_volume",
        settings_key="targetShotVolume",
        native_min_value=0,
        native_max_value=255,
        native_step=1,
        native_unit_of_measurement=UnitOfVolume.MILLILITERS,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    DecentAppShotSettingNumberEntityDescription(
        key="target_group_temp",
        translation_key="target_group_temp",
        settings_key="groupTemp",
        native_min_value=1,
        native_max_value=105,
        native_step=0.5,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    DecentAppShotSettingNumberEntityDescription(
        key="target_steam_temp",
        translation_key="target_steam_temp",
        settings_key="targetSteamTemp",
        native_min_value=100,
        native_max_value=170,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    DecentAppShotSettingNumberEntityDescription(
        key="target_steam_duration",
        translation_key="target_steam_duration",
        settings_key="targetSteamDuration",
        native_min_value=0,
        native_max_value=255,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    DecentAppShotSettingNumberEntityDescription(
        key="target_hot_water_temp",
        translation_key="target_hot_water_temp",
        settings_key="targetHotWaterTemp",
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    DecentAppShotSettingNumberEntityDescription(
        key="target_hot_water_volume",
        translation_key="target_hot_water_volume",
        settings_key="targetHotWaterVolume",
        native_min_value=0,
        native_max_value=255,
        native_step=1,
        native_unit_of_measurement=UnitOfVolume.MILLILITERS,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    DecentAppShotSettingNumberEntityDescription(
        key="target_hot_water_duration",
        translation_key="target_hot_water_duration",
        settings_key="targetHotWaterDuration",
        native_min_value=0,
        native_max_value=255,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
)


class DecentAppShotSettingNumber(NumberEntity, DecentAppEntity):
    """Number entity bound to one ShotSettings field."""

    entity_description: DecentAppShotSettingNumberEntityDescription

    @property
    def native_value(self) -> float | None:
        """Return the current value from the last shot settings frame."""
        return self.coordinator.data.shot_settings.get(self.entity_description.settings_key)

    async def async_set_native_value(self, value: float) -> None:
        """Write the new value as part of the full settings object."""
        await self.coordinator.async_set_shot_setting(self.entity_description.settings_key, value)
