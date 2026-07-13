"""Device info builders for decent_app.

The integration exposes two devices per config entry:
- the espresso machine (via the Decent.app gateway)
- the connected scale (linked to the machine device)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.decent_app.const import DOMAIN
from homeassistant.helpers.device_registry import DeviceInfo

if TYPE_CHECKING:
    from custom_components.decent_app.coordinator import DecentAppDataUpdateCoordinator


def build_machine_device_info(coordinator: DecentAppDataUpdateCoordinator) -> DeviceInfo:
    """Build device info for the espresso machine / gateway."""
    machine_info = coordinator.data.machine_info if coordinator.data else {}
    return DeviceInfo(
        identifiers={(DOMAIN, f"{coordinator.config_entry.entry_id}_machine")},
        name=coordinator.config_entry.title,
        manufacturer="Decent Espresso",
        model=machine_info.get("model") or "DE1",
        serial_number=machine_info.get("serialNumber"),
        sw_version=machine_info.get("version"),
        configuration_url=coordinator.client.base_url,
    )


def build_scale_device_info(coordinator: DecentAppDataUpdateCoordinator) -> DeviceInfo:
    """Build device info for the scale connected to the gateway."""
    devices = coordinator.data.devices if coordinator.data else []
    scale_name = next(
        (device.get("name") for device in devices if device.get("type") == "scale"),
        None,
    )
    return DeviceInfo(
        identifiers={(DOMAIN, f"{coordinator.config_entry.entry_id}_scale")},
        name="Scale",
        manufacturer="Decent Espresso",
        model=scale_name or "Scale",
        via_device=(DOMAIN, f"{coordinator.config_entry.entry_id}_machine"),
    )
