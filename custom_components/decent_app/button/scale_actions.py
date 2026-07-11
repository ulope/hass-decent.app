"""Scale action buttons for decent_app."""

from __future__ import annotations

from custom_components.decent_app.entity import DecentAppScaleEntity
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

ENTITY_DESCRIPTIONS: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="tare_scale",
        translation_key="tare_scale",
    ),
)


class DecentAppScaleButton(ButtonEntity, DecentAppScaleEntity):
    """Button taring the connected scale."""

    async def async_press(self) -> None:
        """Tare the scale."""
        await self.coordinator.async_tare_scale()
