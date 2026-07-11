"""Power switch for decent_app.

Maps the machine's sleep state onto a switch: turning it on wakes the
machine (state idle), turning it off puts it to sleep.
"""

from __future__ import annotations

from custom_components.decent_app.const import MACHINE_STATE_IDLE, MACHINE_STATE_SLEEPING
from custom_components.decent_app.entity import DecentAppEntity
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity, SwitchEntityDescription

ENTITY_DESCRIPTION = SwitchEntityDescription(
    key="power",
    translation_key="power",
    device_class=SwitchDeviceClass.SWITCH,
)


class DecentAppPowerSwitch(SwitchEntity, DecentAppEntity):
    """Switch reflecting whether the machine is awake."""

    @property
    def is_on(self) -> bool | None:
        """Return True while the machine is not sleeping."""
        state = self.coordinator.data.machine_state
        if state is None:
            return None
        return state != MACHINE_STATE_SLEEPING

    async def async_turn_on(self, **_kwargs: object) -> None:
        """Wake the machine."""
        await self.coordinator.async_set_machine_state(MACHINE_STATE_IDLE)

    async def async_turn_off(self, **_kwargs: object) -> None:
        """Put the machine to sleep."""
        await self.coordinator.async_set_machine_state(MACHINE_STATE_SLEEPING)
