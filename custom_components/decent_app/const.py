"""Constants for decent_app."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

# Integration metadata
DOMAIN = "decent_app"
ATTRIBUTION = "Data provided by the Decent.app (ReaPrime) gateway"

# Platform parallel updates - applied to all platforms
PARALLEL_UPDATES = 1

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"

# Default configuration values
DEFAULT_PORT = 8080
DEFAULT_UPDATE_INTERVAL_SECONDS = 60

# Minimum time between coordinator pushes triggered by WebSocket frames.
# Machine snapshots stream at several Hz during a shot; HA does not need
# state updates faster than this.
PUSH_THROTTLE_SECONDS = 1.0

# WebSocket channel paths (relative to ws://host:port/)
WS_MACHINE_SNAPSHOT = "ws/v1/machine/snapshot"
WS_SHOT_SETTINGS = "ws/v1/machine/shotSettings"
WS_WATER_LEVELS = "ws/v1/machine/waterLevels"
WS_SCALE_SNAPSHOT = "ws/v1/scale/snapshot"
WS_DEVICES = "ws/v1/devices"

# Machine states that can be requested via the API (raw API spelling)
MACHINE_STATE_IDLE = "idle"
MACHINE_STATE_SLEEPING = "sleeping"
MACHINE_STATE_ESPRESSO = "espresso"
MACHINE_STATE_HOT_WATER = "hotWater"
MACHINE_STATE_STEAM = "steam"
MACHINE_STATE_FLUSH = "flush"

REQUESTABLE_MACHINE_STATES = [
    MACHINE_STATE_IDLE,
    MACHINE_STATE_SLEEPING,
    MACHINE_STATE_ESPRESSO,
    MACHINE_STATE_HOT_WATER,
    MACHINE_STATE_STEAM,
    MACHINE_STATE_FLUSH,
]

# Union of the machine states reported by the REST and WebSocket APIs,
# normalized to snake_case (see utils.camel_to_snake) for use as enum
# sensor options / translation keys.
MACHINE_STATES = [
    "booting",
    "busy",
    "idle",
    "sleeping",
    "heating",
    "preheating",
    "espresso",
    "hot_water",
    "flush",
    "steam",
    "steam_rinse",
    "skip_step",
    "cleaning",
    "descaling",
    "calibration",
    "self_test",
    "air_purge",
    "transport_mode",
    "needs_water",
    "error",
    "fw_upgrade",
]

# Machine substates, normalized to snake_case ("cleaing_group" is a typo
# in the gateway API enum, preserved here on purpose).
MACHINE_SUBSTATES = [
    "idle",
    "preparing_for_shot",
    "preinfusion",
    "pouring",
    "pouring_done",
    "cleaning_start",
    "cleaing_group",
    "clean_soaking",
    "cleaning_steam",
    "error_na_n",
    "error_inf",
    "error_generic",
    "error_acc",
    "error_tsensor",
    "error_psensor",
    "error_wlevel",
    "error_dip",
    "error_assertion",
    "error_unsafe",
    "error_invalid_param",
    "error_flash",
    "error_oom",
    "error_deadline",
    "error_hi_current",
    "error_lo_current",
    "error_boot_fill",
    "error_no_ac",
]
