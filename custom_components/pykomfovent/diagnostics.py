from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import KomfoventCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    coordinator: KomfoventCoordinator = hass.data[DOMAIN][entry.entry_id]

    data = coordinator.data
    if data is None:
        return {"error": "No data available"}

    return {
        "config_entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "domain": entry.domain,
            "title": entry.title,
        },
        "device": {
            "host": coordinator.host,
        },
        "state": {
            "mode": data.mode,
            "supply_temp": data.supply_temp,
            "extract_temp": data.extract_temp,
            "outdoor_temp": data.outdoor_temp,
            "supply_temp_setpoint": data.supply_temp_setpoint,
            "extract_temp_setpoint": data.extract_temp_setpoint,
            "supply_fan_percent": data.supply_fan_percent,
            "extract_fan_percent": data.extract_fan_percent,
            "filter_contamination": data.filter_contamination,
            "power_consumption": data.power_consumption,
            "flags": data.flags,
            "flags_binary": bin(data.flags),
            "is_on": data.is_on,
            "eco_mode": data.eco_mode,
            "heating_active": data.heating_active,
        },
    }
