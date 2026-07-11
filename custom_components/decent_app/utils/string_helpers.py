"""String helper utilities for decent_app."""

from __future__ import annotations

import re

_CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def camel_to_snake(value: str) -> str:
    """
    Convert a camelCase API value to snake_case.

    Used to normalize the gateway's machine state/substate enum values
    (e.g. "hotWater" → "hot_water") so they are valid Home Assistant
    translation keys.
    """
    return _CAMEL_BOUNDARY.sub("_", value).lower()
