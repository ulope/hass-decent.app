"""Brew profile select entity for decent_app.

Options are the visible profiles stored on the gateway. Selecting a
profile updates the current workflow, which uploads the profile to the
machine as one atomic operation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.decent_app.entity import DecentAppEntity
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.exceptions import HomeAssistantError

if TYPE_CHECKING:
    from custom_components.decent_app.coordinator import DecentAppDataUpdateCoordinator

ENTITY_DESCRIPTION = SelectEntityDescription(
    key="brew_profile",
    translation_key="brew_profile",
)


class DecentAppProfileSelect(SelectEntity, DecentAppEntity):
    """Select entity for choosing the active brew profile."""

    def __init__(self, coordinator: DecentAppDataUpdateCoordinator) -> None:
        """Initialize the profile select."""
        super().__init__(coordinator, ENTITY_DESCRIPTION)

    def _title_to_id(self) -> dict[str, str]:
        """Map visible profile titles to profile IDs (first title wins)."""
        mapping: dict[str, str] = {}
        for record in self.coordinator.data.profiles:
            if record.get("visibility") not in (None, "visible"):
                continue
            title = (record.get("profile") or {}).get("title")
            profile_id = record.get("id")
            if title and profile_id and title not in mapping:
                mapping[title] = profile_id
        return mapping

    @property
    def options(self) -> list[str]:
        """Return the available profile titles."""
        return sorted(self._title_to_id(), key=str.casefold)

    @property
    def current_option(self) -> str | None:
        """Return the title of the profile in the current workflow."""
        workflow_profile = self.coordinator.data.workflow.get("profile") or {}
        title = workflow_profile.get("title")
        if title in self._title_to_id():
            return title
        return None

    async def async_select_option(self, option: str) -> None:
        """Apply the selected profile via the workflow."""
        profile_id = self._title_to_id().get(option)
        if profile_id is None:
            msg = f"Unknown profile: {option}"
            raise HomeAssistantError(msg)
        await self.coordinator.async_select_profile(profile_id)
