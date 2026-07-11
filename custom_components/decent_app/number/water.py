"""Water refill threshold number entity for decent_app."""

from __future__ import annotations

from custom_components.decent_app.entity import DecentAppEntity
from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import EntityCategory

ENTITY_DESCRIPTIONS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key="water_refill_level",
        translation_key="water_refill_level",
        native_min_value=0,
        native_max_value=70,
        native_step=1,
        native_unit_of_measurement="mm",
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
)


class DecentAppWaterRefillNumber(NumberEntity, DecentAppEntity):
    """Number entity for the water tank refill warning threshold."""

    @property
    def native_value(self) -> float | None:
        """Return the current refill threshold from the water levels frame."""
        return self.coordinator.data.water_levels.get("refillLevel")

    async def async_set_native_value(self, value: float) -> None:
        """Set the refill threshold on the machine."""
        await self.coordinator.async_set_water_refill_level(value)
