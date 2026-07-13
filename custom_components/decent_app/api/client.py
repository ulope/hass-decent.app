"""
REST API client for the Decent.app (ReaPrime) gateway.

The gateway exposes a local HTTP API on the tablet running Decent.app
(default port 8080). This client wraps the REST v1 endpoints used by the
integration. Live telemetry is delivered via WebSockets instead - see
websocket.py.

API specification:
https://github.com/tadelv/reaprime/blob/main/assets/api/rest_v1.yml
"""

from __future__ import annotations

import asyncio
import socket
from typing import TYPE_CHECKING, Any

import aiohttp

if TYPE_CHECKING:
    from collections.abc import Mapping

REQUEST_TIMEOUT_SECONDS = 10


class DecentAppApiClientError(Exception):
    """Base exception to indicate a general API error."""


class DecentAppApiClientCommunicationError(
    DecentAppApiClientError,
):
    """Exception to indicate a communication error with the API."""


class DecentAppApiClient:
    """
    Client for the Decent.app gateway REST API.

    The API requires no authentication - the gateway is reachable on the
    local network only. All live telemetry (pressure, flow, temperatures,
    scale weight, ...) is consumed via the WebSocket channels; this client
    covers configuration reads and command writes.

    Attributes:
        _host: Hostname or IP address of the tablet running Decent.app.
        _port: TCP port of the gateway (default 8080).
        _session: The aiohttp ClientSession for making requests.

    """

    def __init__(
        self,
        host: str,
        port: int,
        session: aiohttp.ClientSession,
    ) -> None:
        """
        Initialize the API client.

        Args:
            host: Hostname or IP address of the tablet running Decent.app.
            port: TCP port of the gateway.
            session: The aiohttp ClientSession to use for requests.

        """
        self._host = host
        self._port = port
        self._session = session

    @property
    def base_url(self) -> str:
        """Return the HTTP base URL of the gateway."""
        return f"http://{self._host}:{self._port}"

    @property
    def websocket_base_url(self) -> str:
        """Return the WebSocket base URL of the gateway."""
        return f"ws://{self._host}:{self._port}"

    async def async_get_app_info(self) -> dict[str, Any]:
        """Get gateway build information (version, commit, local IP)."""
        return await self._api_wrapper("get", "/api/v1/info")

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Get the list of known devices (machine, scale, sensors)."""
        return await self._api_wrapper("get", "/api/v1/devices")

    async def async_scan_devices(self) -> None:
        """Trigger a device scan with automatic connection."""
        await self._api_wrapper("get", "/api/v1/devices/scan", params={"quick": "true"})

    async def async_get_machine_info(self) -> dict[str, Any]:
        """Get information about the connected machine (model, serial, firmware)."""
        return await self._api_wrapper("get", "/api/v1/machine/info")

    async def async_get_machine_state(self) -> dict[str, Any]:
        """Get the current machine state snapshot."""
        return await self._api_wrapper("get", "/api/v1/machine/state")

    async def async_set_machine_state(self, state: str) -> None:
        """
        Request a machine state change.

        Args:
            state: The requested state, e.g. idle, sleeping, espresso,
                hotWater, steam or flush.

        """
        await self._api_wrapper("put", f"/api/v1/machine/state/{state}")

    async def async_set_shot_settings(self, settings: Mapping[str, Any]) -> None:
        """Update the machine shot settings (steam/hot water/shot targets)."""
        await self._api_wrapper("post", "/api/v1/machine/shotSettings", data=dict(settings))

    async def async_set_water_refill_level(self, refill_level: float) -> None:
        """Set the water tank refill warning threshold in mm."""
        await self._api_wrapper(
            "post",
            "/api/v1/machine/waterLevels",
            data={"refillLevel": refill_level},
        )

    async def async_tare_scale(self) -> None:
        """Tare the connected scale."""
        await self._api_wrapper("put", "/api/v1/scale/tare")

    async def async_get_workflow(self) -> dict[str, Any]:
        """Get the current workflow (profile, steam/hot water settings, dose)."""
        return await self._api_wrapper("get", "/api/v1/workflow")

    async def async_update_workflow(self, workflow: Mapping[str, Any]) -> dict[str, Any]:
        """
        Update the current workflow.

        Only provided fields are changed; this is the recommended way to
        apply a new profile or brewing parameters as one atomic operation.
        """
        return await self._api_wrapper("put", "/api/v1/workflow", data=dict(workflow))

    async def async_get_profiles(self) -> list[dict[str, Any]]:
        """Get all stored profile records."""
        return await self._api_wrapper("get", "/api/v1/profiles")

    async def async_get_profile(self, profile_id: str) -> dict[str, Any]:
        """Get a single profile record by its ID."""
        return await self._api_wrapper("get", f"/api/v1/profiles/{profile_id}")

    async def _api_wrapper(
        self,
        method: str,
        path: str,
        data: dict | None = None,
        params: dict | None = None,
    ) -> Any:
        """
        Wrapper for API requests with error handling.

        Args:
            method: The HTTP method (get, post, put, delete).
            path: The URL path relative to the gateway base URL.
            data: Optional JSON body to send with the request.
            params: Optional query parameters.

        Returns:
            The decoded JSON response, or None for empty responses.

        Raises:
            DecentAppApiClientCommunicationError: If communication fails.
            DecentAppApiClientError: For HTTP or other API errors.

        """
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT_SECONDS):
                response = await self._session.request(
                    method=method,
                    url=f"{self.base_url}{path}",
                    json=data,
                    params=params,
                )
                if response.status >= 400:
                    body = await response.text()
                    msg = f"API request {method.upper()} {path} failed with status {response.status}: {body[:200]}"
                    raise DecentAppApiClientError(msg)
                if response.content_type == "application/json":
                    return await response.json()
                return None

        except TimeoutError as exception:
            msg = f"Timeout communicating with Decent.app gateway - {exception}"
            raise DecentAppApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror, OSError) as exception:
            msg = f"Error communicating with Decent.app gateway - {exception}"
            raise DecentAppApiClientCommunicationError(msg) from exception
