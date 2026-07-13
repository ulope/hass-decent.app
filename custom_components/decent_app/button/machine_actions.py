"""Machine action buttons for decent_app.

Each button requests a machine state change via the gateway. Note that
machines with a Group Head Controller (GHC) refuse remote start of
espresso/steam/hot water for safety reasons; the gateway returns an error
in that case which is surfaced to the user.
"""

from __future__ import annotations

from dataclasses import dataclass

from custom_components.decent_app.const import (
    MACHINE_STATE_ESPRESSO,
    MACHINE_STATE_FLUSH,
    MACHINE_STATE_HOT_WATER,
    MACHINE_STATE_IDLE,
    MACHINE_STATE_SLEEPING,
    MACHINE_STATE_STEAM,
)
from custom_components.decent_app.entity import DecentAppEntity
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription


@dataclass(frozen=True, kw_only=True)
class DecentAppMachineButtonEntityDescription(ButtonEntityDescription):
    """Describes a machine action button and the state it requests."""

    target_state: str


ENTITY_DESCRIPTIONS: tuple[DecentAppMachineButtonEntityDescription, ...] = (
    DecentAppMachineButtonEntityDescription(
        key="start_espresso",
        translation_key="start_espresso",
        target_state=MACHINE_STATE_ESPRESSO,
    ),
    DecentAppMachineButtonEntityDescription(
        key="start_steam",
        translation_key="start_steam",
        target_state=MACHINE_STATE_STEAM,
    ),
    DecentAppMachineButtonEntityDescription(
        key="start_hot_water",
        translation_key="start_hot_water",
        target_state=MACHINE_STATE_HOT_WATER,
    ),
    DecentAppMachineButtonEntityDescription(
        key="start_flush",
        translation_key="start_flush",
        target_state=MACHINE_STATE_FLUSH,
    ),
    DecentAppMachineButtonEntityDescription(
        key="stop",
        translation_key="stop",
        target_state=MACHINE_STATE_IDLE,
    ),
    DecentAppMachineButtonEntityDescription(
        key="sleep",
        translation_key="sleep",
        target_state=MACHINE_STATE_SLEEPING,
    ),
)


class DecentAppMachineButton(ButtonEntity, DecentAppEntity):
    """Button requesting a machine state change."""

    entity_description: DecentAppMachineButtonEntityDescription

    async def async_press(self) -> None:
        """Request the machine state change."""
        await self.coordinator.async_set_machine_state(self.entity_description.target_state)
