"""
Core DataUpdateCoordinator implementation for decent_app.

The Decent.app gateway is primarily push-based: live telemetry (machine
snapshots, shot settings, water levels, scale weight, device state) arrives
via WebSocket channels and is merged into the coordinator state as frames
come in. A slow REST poll acts as fallback and refreshes data that has no
WebSocket channel (machine info, workflow, stored profiles).

WebSocket pushes are throttled to PUSH_THROTTLE_SECONDS because machine and
scale snapshots stream at several Hz during a shot. The REST poll runs on
its own timer (instead of the coordinator's update_interval) so that
frequent pushes cannot starve it.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
import time
from typing import TYPE_CHECKING, Any

from custom_components.decent_app.api import DecentAppApiClientError
from custom_components.decent_app.const import (
    DEFAULT_UPDATE_INTERVAL_SECONDS,
    DOMAIN,
    LOGGER,
    PUSH_THROTTLE_SECONDS,
    WS_DEVICES,
    WS_MACHINE_SNAPSHOT,
    WS_SCALE_SNAPSHOT,
    WS_SHOT_SETTINGS,
    WS_WATER_LEVELS,
)
from homeassistant.core import CALLBACK_TYPE, callback
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .commands import DecentAppCommandsMixin
from .state import DecentAppState

if TYPE_CHECKING:
    from datetime import datetime

    from custom_components.decent_app.api import DecentAppApiClient, DecentAppWebsocketListener
    from custom_components.decent_app.data import DecentAppConfigEntry
    from homeassistant.core import HomeAssistant


class DecentAppDataUpdateCoordinator(DecentAppCommandsMixin, DataUpdateCoordinator[DecentAppState]):
    """
    Coordinator merging WebSocket pushes with a REST fallback poll.

    Data flow:
    - WebSocket frames update individual fields of the internal state and
      trigger (throttled) pushes to entities.
    - A periodic REST poll refreshes the device list, machine info,
      workflow and stored profiles, and doubles as a liveness check for
      the gateway (a failed poll marks all entities unavailable).
    """

    config_entry: DecentAppConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: DecentAppConfigEntry,
        client: DecentAppApiClient,
        websocket: DecentAppWebsocketListener,
    ) -> None:
        """
        Initialize the coordinator.

        Args:
            hass: The Home Assistant instance.
            config_entry: The config entry for this gateway.
            client: REST API client for the gateway.
            websocket: WebSocket listener (not yet started).

        """
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=None,  # REST polling runs on its own timer
            always_update=False,
        )
        self.client = client
        self.websocket = websocket
        self._state = DecentAppState()
        self._last_push = 0.0
        self._cancel_flush: CALLBACK_TYPE | None = None
        self._unsub_poll: CALLBACK_TYPE | None = None

    @property
    def state(self) -> DecentAppState:
        """Return the mutable internal state (for the commands mixin)."""
        return self._state

    async def _async_setup(self) -> None:
        """Wire up WebSocket channels and start the fallback poll timer."""
        self.websocket.subscribe(WS_MACHINE_SNAPSHOT, self._handle_machine_snapshot)
        self.websocket.subscribe(WS_SHOT_SETTINGS, self._handle_shot_settings)
        self.websocket.subscribe(WS_WATER_LEVELS, self._handle_water_levels)
        self.websocket.subscribe(WS_SCALE_SNAPSHOT, self._handle_scale_snapshot)
        self.websocket.subscribe(WS_DEVICES, self._handle_devices)
        self.websocket.async_start()

        self._unsub_poll = async_track_time_interval(
            self.hass,
            self._async_scheduled_poll,
            timedelta(seconds=DEFAULT_UPDATE_INTERVAL_SECONDS),
        )

    async def async_shutdown(self) -> None:
        """Stop the WebSocket listener and poll timer on unload."""
        if self._unsub_poll is not None:
            self._unsub_poll()
            self._unsub_poll = None
        if self._cancel_flush is not None:
            self._cancel_flush()
            self._cancel_flush = None
        await self.websocket.async_stop()
        await super().async_shutdown()

    async def _async_scheduled_poll(self, _now: datetime) -> None:
        """Run the periodic REST fallback poll."""
        await self.async_refresh()

    async def _async_update_data(self) -> DecentAppState:
        """
        Poll REST endpoints and merge the results into the state.

        The device list is the liveness check: if it fails, the gateway is
        unreachable and the update is marked failed. Machine-specific
        endpoints are best-effort because they error while no machine is
        connected to the gateway.
        """
        state = replace(self._state)
        try:
            state.devices = await self.client.async_get_devices()
        except DecentAppApiClientError as exception:
            raise UpdateFailed(f"Cannot reach Decent.app gateway: {exception}") from exception

        if not state.app_info:
            state.app_info = await self._optional_fetch(self.client.async_get_app_info) or {}

        if state.machine_connected:
            machine_info = await self._optional_fetch(self.client.async_get_machine_info)
            if machine_info:
                state.machine_info = machine_info
            snapshot = await self._optional_fetch(self.client.async_get_machine_state)
            if snapshot:
                state.machine_snapshot = snapshot

        workflow = await self._optional_fetch(self.client.async_get_workflow)
        if workflow:
            state.workflow = workflow
        profiles = await self._optional_fetch(self.client.async_get_profiles)
        if profiles is not None:
            state.profiles = profiles

        self._state = state
        self._last_push = time.monotonic()
        return state

    async def _optional_fetch(self, fetcher: Any) -> Any:
        """Fetch an endpoint that may legitimately fail; return None on error."""
        try:
            return await fetcher()
        except DecentAppApiClientError as exception:
            LOGGER.debug("Optional fetch %s failed: %s", getattr(fetcher, "__name__", fetcher), exception)
            return None

    # --- WebSocket frame handlers -------------------------------------------------

    @callback
    def _handle_machine_snapshot(self, payload: dict[str, Any]) -> None:
        """Handle a machine snapshot frame (streams at high rate during shots)."""
        self._state.machine_snapshot = payload
        self.push_state()

    @callback
    def _handle_shot_settings(self, payload: dict[str, Any]) -> None:
        """Handle a shot settings frame."""
        self._state.shot_settings = payload
        self.push_state()

    @callback
    def _handle_water_levels(self, payload: dict[str, Any]) -> None:
        """Handle a water levels frame."""
        self._state.water_levels = payload
        self.push_state()

    @callback
    def _handle_scale_snapshot(self, payload: dict[str, Any]) -> None:
        """
        Handle a scale channel frame.

        The channel multiplexes status frames ({"status": ...}) emitted on
        connection state changes and snapshot frames (weight/flow/battery)
        emitted while a scale is connected.
        """
        if "status" in payload:
            self._state.scale_connected = payload.get("status") == "connected"
        else:
            self._state.scale_snapshot = payload
            self._state.scale_connected = True
        self.push_state()

    @callback
    def _handle_devices(self, payload: dict[str, Any]) -> None:
        """Handle a devices state frame (device list and connection states)."""
        devices = payload.get("devices")
        if isinstance(devices, list):
            self._state.devices = devices
        self.push_state()

    # --- Push throttling ----------------------------------------------------------

    @callback
    def push_state(self) -> None:
        """
        Push the current state to entities, throttled to PUSH_THROTTLE_SECONDS.

        If a push happened too recently, a trailing flush is scheduled so
        the final frame of a burst is never lost.
        """
        elapsed = time.monotonic() - self._last_push
        if elapsed >= PUSH_THROTTLE_SECONDS:
            self._flush_state()
        elif self._cancel_flush is None:
            self._cancel_flush = async_call_later(
                self.hass,
                PUSH_THROTTLE_SECONDS - elapsed,
                self._async_delayed_flush,
            )

    @callback
    def _async_delayed_flush(self, _now: datetime) -> None:
        """Flush the most recent state after the throttle window has passed."""
        self._cancel_flush = None
        self._flush_state()

    @callback
    def _flush_state(self) -> None:
        """Hand a snapshot of the current state to the coordinator machinery."""
        if self._cancel_flush is not None:
            self._cancel_flush()
            self._cancel_flush = None
        self._last_push = time.monotonic()
        self.async_set_updated_data(replace(self._state))
