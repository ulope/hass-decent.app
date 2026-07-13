"""
API package for decent_app.

Architecture:
    Three-layer data flow: Entities → Coordinator → API Client.
    Only the coordinator should call the API client. Entities must never
    import or call the API client directly.

Modules:
    client.py    - REST client for commands and configuration
    websocket.py - WebSocket listener for live telemetry (preferred source)

Exception hierarchy:
    DecentAppApiClientError (base)
    └── DecentAppApiClientCommunicationError (network/timeout)

Coordinator exception mapping:
    ApiClientCommunicationError → UpdateFailed (auto-retry)
    ApiClientError              → UpdateFailed (auto-retry)
"""

from .client import DecentAppApiClient, DecentAppApiClientCommunicationError, DecentAppApiClientError
from .websocket import DecentAppWebsocketListener

__all__ = [
    "DecentAppApiClient",
    "DecentAppApiClientCommunicationError",
    "DecentAppApiClientError",
    "DecentAppWebsocketListener",
]
