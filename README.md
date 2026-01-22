# Komfovent C6 for Home Assistant

[![CI](https://github.com/mostaszewski/hass-pykomfovent/actions/workflows/ci.yml/badge.svg)](https://github.com/mostaszewski/hass-pykomfovent/actions/workflows/ci.yml)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/github/license/mostaszewski/hass-pykomfovent)](LICENSE)

Home Assistant integration for Komfovent C6 ventilation units.

> **Support:** [Open an issue](https://github.com/mostaszewski/hass-pykomfovent/issues) or contact pykomfovent@ostaszewski.pl

## Features

- 27 sensors (temperatures, fans, energy, filter status)
- 2 binary sensors (filter warning, heating active)
- Mode control (Away, Normal, Intensive, Boost)
- Temperature setpoint control
- Schedule management
- 42 advanced configuration entities (per-mode settings)
- Device triggers for automations
- Custom Lovelace card
- Autodiscovery
- Energy dashboard support

![Komfovent Card](https://raw.githubusercontent.com/mostaszewski/hass-pykomfovent/main/images/card.png)

---

## Installation

### HACS (Recommended)

1. Open HACS → three dots → **Custom repositories**
2. Add `https://github.com/mostaszewski/hass-pykomfovent` as **Integration**
3. Search "Komfovent" and install
4. Restart Home Assistant

### Manual

Copy `custom_components/pykomfovent` to your `config/custom_components/` and restart.

---

## Configuration

1. **Settings** → **Devices & Services** → **Add Integration**
2. Search "Komfovent"
3. Enter details:

| Field | Description |
|-------|-------------|
| Host | IP address (empty for autodiscovery) |
| Username | Web interface username |
| Password | Web interface password |
| Scan Interval | Update frequency (default: 30s) |

---

## Entities

### Sensors

| Entity | Unit | Description |
|--------|------|-------------|
| Mode | - | Current operating mode |
| Supply/Extract/Outdoor Temperature | °C | Air temperatures |
| Supply/Extract Fan | % | Fan speeds |
| Filter Contamination | % | Filter dirt level |
| Heat Exchanger Efficiency | % | Recovery efficiency |
| Power Consumption | W | Current power usage |
| Energy Consumed Daily/Monthly/Total | kWh | Energy statistics |
| Energy Recovered Daily/Monthly/Total | kWh | Heat recovery statistics |

### Binary Sensors

| Entity | Description |
|--------|-------------|
| Filter Needs Cleaning | True when filter > 80% dirty |
| Heating Active | True when heater is running |

### Controls

| Entity | Type | Range |
|--------|------|-------|
| Mode | Select | Away, Normal, Intensive, Boost |
| Supply Temperature Setpoint | Number | 10-30°C |

### Mode Configuration (disabled by default)

42 entities for advanced per-mode settings:
- Fan speeds per mode (14 numbers)
- Temperature setpoints per mode (8 numbers)
- Humidity setpoints per mode (4 numbers)
- Electric heater per mode (8 switches)
- ECO settings (5 entities)
- AUTO settings (3 entities)

Enable via: **Devices & Services** → **Komfovent** → **Entities** → **Show disabled**

---

## Services

### pykomfovent.set_mode

```yaml
service: pykomfovent.set_mode
data:
  mode: intensive  # away, normal, intensive, boost
  device_id: abc123  # optional, targets specific device
```

### pykomfovent.set_temperature

```yaml
service: pykomfovent.set_temperature
data:
  temperature: 22.5
  device_id: abc123  # optional
```

### pykomfovent.set_schedule

```yaml
service: pykomfovent.set_schedule
data:
  program: 0
  row: 0
  weekdays: 31  # Mon-Fri (bitmask: Mon=1, Tue=2, Wed=4, Thu=8, Fri=16, Sat=32, Sun=64)
  entries:
    - mode: away
      start: "00:00"
      stop: "06:00"
    - mode: normal
      start: "06:00"
      stop: "22:00"
    - mode: away
      start: "22:00"
      stop: "24:00"
  device_id: abc123  # optional
```

### pykomfovent.get_schedule

```yaml
service: pykomfovent.get_schedule
data:
  device_id: abc123  # optional
response_variable: schedule
```

> **Note:** If `device_id` is omitted, services apply to all configured devices.

---

## Automation Examples

### Filter Alert

```yaml
automation:
  - alias: "Filter Alert"
    trigger:
      - platform: device
        device_id: <your_device_id>
        domain: pykomfovent
        type: filter_warning
    action:
      - service: notify.mobile_app
        data:
          message: "Ventilation filter needs cleaning!"
```

### Boost on High CO2

```yaml
automation:
  - alias: "Boost on CO2"
    trigger:
      - platform: numeric_state
        entity_id: sensor.co2
        above: 1000
    action:
      - service: pykomfovent.set_mode
        data:
          mode: boost
```

### Night Mode

```yaml
automation:
  - alias: "Night Mode"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: pykomfovent.set_mode
        data:
          mode: away
      - service: pykomfovent.set_temperature
        data:
          temperature: 20
```

---

## Lovelace Card

1. **Settings** → **Dashboards** → **Resources**
2. Add: `/komfovent/komfovent-card.js` (JavaScript Module)
3. Use in dashboard:

```yaml
type: custom:komfovent-card
entity: sensor.komfovent_192_168_0_137_mode
```

---

## Dashboard Examples

### Simple Status Card

```yaml
type: entities
title: Ventilation
entities:
  - entity: select.komfovent_192_168_0_137_mode_select
  - entity: number.komfovent_192_168_0_137_supply_temp_setpoint
  - entity: sensor.komfovent_192_168_0_137_supply_temperature
  - entity: sensor.komfovent_192_168_0_137_outdoor_temperature
  - entity: sensor.komfovent_192_168_0_137_filter_contamination
  - entity: binary_sensor.komfovent_192_168_0_137_filter_dirty
```

### Glance Card

```yaml
type: glance
title: Ventilation
entities:
  - entity: sensor.komfovent_192_168_0_137_mode
    name: Mode
  - entity: sensor.komfovent_192_168_0_137_supply_temperature
    name: Supply
  - entity: sensor.komfovent_192_168_0_137_outdoor_temperature
    name: Outdoor
  - entity: sensor.komfovent_192_168_0_137_supply_fan
    name: Fan
```

### Energy Card

```yaml
type: energy-distribution
title: Ventilation Energy
entities:
  - sensor.komfovent_192_168_0_137_power_consumption
  - sensor.komfovent_192_168_0_137_heat_recovery_power
```

### Mode Buttons

```yaml
type: horizontal-stack
cards:
  - type: button
    name: Away
    icon: mdi:home-export-outline
    tap_action:
      action: call-service
      service: pykomfovent.set_mode
      data:
        mode: away
  - type: button
    name: Normal
    icon: mdi:home
    tap_action:
      action: call-service
      service: pykomfovent.set_mode
      data:
        mode: normal
  - type: button
    name: Intensive
    icon: mdi:fan
    tap_action:
      action: call-service
      service: pykomfovent.set_mode
      data:
        mode: intensive
  - type: button
    name: Boost
    icon: mdi:fan-plus
    tap_action:
      action: call-service
      service: pykomfovent.set_mode
      data:
        mode: boost
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Integration not loading | Check logs, verify device IP is reachable |
| Entities unavailable | Check network, verify credentials |
| Mode config not visible | Enable disabled entities in device settings |

---

## Requirements

- Home Assistant 2024.1.0+
- Komfovent C6 ventilation unit with web interface

## Library

This integration uses [pykomfovent](https://github.com/mostaszewski/pykomfovent) for device communication.

## License

MIT
