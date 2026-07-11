# Decent.app

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

Home Assistant integration for the [Decent Espresso](https://decentespresso.com/) machine via the new
**Decent.app ([ReaPrime](https://github.com/tadelv/reaprime)) gateway** running on the tablet attached to the machine.

The integration connects to the gateway's local REST + WebSocket API. Live telemetry
(machine state, pressure, flow, temperatures, water level, scale weight) is streamed
over WebSockets, so entities update in real time during a shot without polling.

## ✨ Features

- **Local push**: live machine and scale telemetry via the gateway's WebSocket channels
- **Machine control**: start espresso / steam / hot water / flush, stop, sleep and wake
- **Brew profile selection**: pick any profile stored on the tablet directly from Home Assistant
- **Shot settings**: adjust target shot volume, brew/steam/hot-water temperatures, durations and volumes
- **Scale support**: weight, flow and battery of the connected scale, plus a tare button
- **Water management**: tank level sensor, low-water alert, refill threshold setting

**This integration will set up the following platforms.**

| Platform        | Description                                                                    |
| --------------- | ------------------------------------------------------------------------------ |
| `sensor`        | Machine state, pressure, flow, temperatures, water level, scale weight/battery |
| `binary_sensor` | Machine/scale connectivity, water level low                                    |
| `button`        | Start espresso/steam/hot water/flush, stop, sleep, tare scale                  |
| `switch`        | Power (wake/sleep)                                                             |
| `select`        | Brew profile                                                                   |
| `number`        | Shot settings (volumes, temperatures, durations), water refill threshold       |

> [!NOTE]
> Machines with a Group Head Controller (GHC) do not allow starting espresso, steam or
> hot water remotely — the firmware requires using the GHC buttons. Stopping, sleeping
> and all settings still work.

## 🚀 Quick Start

### Prerequisites

- A Decent Espresso machine with a tablet running **Decent.app / ReaPrime** (the gateway
  serves its API on port `8080` by default)
- The tablet must be reachable from Home Assistant on your local network

### Step 1: Install the Integration

**Prerequisites:** This integration requires [HACS](https://hacs.xyz/) (Home Assistant Community Store) to be installed.

Click the button below to open the integration directly in HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ulope&repository=hass-decent.app&category=integration)

Then:

1. Click "Download" to install the integration
2. **Restart Home Assistant** (required after installation)

<details>
<summary><strong>Manual Installation (Advanced)</strong></summary>

If you prefer not to use HACS:

1. Download the `custom_components/decent_app/` folder from this repository
2. Copy it to your Home Assistant's `custom_components/` directory
3. Restart Home Assistant

</details>

### Step 2: Add and Configure the Integration

Click the button below to open the configuration dialog:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=decent_app)

Or manually: **Settings** → **Devices & Services** → **"+ Add Integration"** → search for "Decent.app".

Setup only asks for:

| Name | Required | Description                                             |
| ---- | -------- | ------------------------------------------------------- |
| Host | Yes      | IP address or hostname of the tablet running Decent.app |
| Port | Yes      | Gateway API port (default `8080`)                       |

No credentials are needed — the gateway API is local and unauthenticated.
You can change the address later via **Reconfigure**.

## Custom Services

### `decent_app.set_machine_state`

Request a machine state change directly (useful in automations).

```yaml
service: decent_app.set_machine_state
data:
  state: espresso # idle | sleeping | espresso | hotWater | steam | flush
```

## Troubleshooting

- **"Unable to connect" during setup**: verify the tablet's IP and that
  `http://<tablet-ip>:8080/api/v1/info` is reachable from the Home Assistant host.
- **Entities unavailable**: the machine entities become unavailable while the machine is
  disconnected from the gateway (e.g. Bluetooth off); the scale entities while no scale
  is connected. Check the **Machine connected** / **Scale connected** binary sensors.
- **Debug logging**: add to `configuration.yaml`:

  ```yaml
  logger:
    logs:
      custom_components.decent_app: debug
  ```

## 🛠️ Development

This repository is based on the [HACS integration blueprint](https://github.com/jpawlowski/hacs.integration_blueprint)
and keeps its development tooling:

```bash
script/setup/bootstrap  # one-time environment setup
script/develop          # run Home Assistant with the integration
script/check            # type-check + lint + spell
script/test             # run tests
```

API documentation of the gateway:

- [REST v1 spec](https://github.com/tadelv/reaprime/blob/main/assets/api/rest_v1.yml)
- [WebSocket v1 spec](https://github.com/tadelv/reaprime/blob/main/assets/api/websocket_v1.yml)

---

## 🤖 AI-Assisted Development

> [!NOTE]
> **Transparency Notice:** This integration was developed with assistance from AI coding agents. While the codebase follows Home Assistant Core standards, AI-generated code may not be reviewed or tested to the same extent as manually written code. If you encounter unexpected behavior, please [open an issue](../../issues) on GitHub.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [@ulope][user_profile]**

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/ulope/hass-decent.app.svg?style=for-the-badge
[commits]: https://github.com/ulope/hass-decent.app/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/ulope/hass-decent.app.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40ulope-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/ulope/hass-decent.app.svg?style=for-the-badge
[releases]: https://github.com/ulope/hass-decent.app/releases
[user_profile]: https://github.com/ulope
