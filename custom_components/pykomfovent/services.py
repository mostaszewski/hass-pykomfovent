import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, MODES
from .coordinator import KomfoventCoordinator
from .schedule import build_schedule_commands, parse_schedule_config

SERVICE_SET_MODE = "set_mode"
SERVICE_SET_TEMPERATURE = "set_temperature"
SERVICE_GET_SCHEDULE = "get_schedule"
SERVICE_SET_SCHEDULE = "set_schedule"

SERVICE_SET_MODE_SCHEMA = vol.Schema(
    {
        vol.Required("mode"): vol.In(list(MODES.keys())),
        vol.Optional("device_id"): str,
    }
)

SERVICE_SET_TEMPERATURE_SCHEMA = vol.Schema(
    {
        vol.Required("temperature"): vol.All(vol.Coerce(float), vol.Range(min=10, max=30)),
        vol.Optional("device_id"): str,
    }
)

SERVICE_SET_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required("program"): vol.All(vol.Coerce(int), vol.Range(min=0, max=3)),
        vol.Required("row"): vol.All(vol.Coerce(int), vol.Range(min=0, max=3)),
        vol.Required("weekdays"): vol.All(vol.Coerce(int), vol.Range(min=0, max=127)),
        vol.Required("entries"): [
            {
                vol.Required("mode"): vol.In(["away", "normal", "intensive", "boost"]),
                vol.Required("start"): str,
                vol.Required("stop"): str,
            }
        ],
        vol.Optional("device_id"): str,
    }
)

SERVICE_GET_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Optional("device_id"): str,
    }
)


def _get_coordinators(hass: HomeAssistant, device_id: str | None) -> list[KomfoventCoordinator]:
    coordinators: list[KomfoventCoordinator] = []
    for coordinator in hass.data.get(DOMAIN, {}).values():
        if not isinstance(coordinator, KomfoventCoordinator):
            continue
        if device_id is None:
            coordinators.append(coordinator)
        else:
            device_registry = dr.async_get(hass)
            device = device_registry.async_get(device_id)
            if device and (DOMAIN, coordinator.host) in device.identifiers:
                coordinators.append(coordinator)
    return coordinators


async def async_setup_services(hass: HomeAssistant) -> None:
    async def handle_set_mode(call: ServiceCall) -> None:
        mode = call.data["mode"]
        device_id = call.data.get("device_id")
        for coordinator in _get_coordinators(hass, device_id):
            await coordinator.client.set_mode(mode)
            await coordinator.async_request_refresh()

    async def handle_set_temperature(call: ServiceCall) -> None:
        temp = call.data["temperature"]
        device_id = call.data.get("device_id")
        for coordinator in _get_coordinators(hass, device_id):
            await coordinator.client.set_supply_temp(temp)
            await coordinator.async_request_refresh()

    async def handle_get_schedule(call: ServiceCall) -> dict:
        device_id = call.data.get("device_id")
        for coordinator in _get_coordinators(hass, device_id):
            raw = await coordinator.client.get_schedule()
            schedules = parse_schedule_config(raw)
            return {
                "current_program": raw.get("current_program", 0),
                "schedules": [
                    {
                        "program": s.program,
                        "rows": [
                            {
                                "weekdays": r.weekdays,
                                "weekday_mask": r.weekday_mask,
                                "entries": [
                                    {
                                        "mode": e.mode.name.lower(),
                                        "start": f"{e.start_hour:02d}:{e.start_minute:02d}",
                                        "stop": f"{e.stop_hour:02d}:{e.stop_minute:02d}",
                                    }
                                    for e in r.entries
                                ],
                            }
                            for r in s.rows
                        ],
                    }
                    for s in schedules
                ],
            }
        return {}

    async def handle_set_schedule(call: ServiceCall) -> None:
        program = call.data["program"]
        row = call.data["row"]
        weekdays = call.data["weekdays"]
        entries_data = call.data["entries"]
        device_id = call.data.get("device_id")

        mode_map = {"away": 1, "normal": 2, "intensive": 3, "boost": 4}
        entries = []
        for e in entries_data:
            start_parts = e["start"].split(":")
            stop_parts = e["stop"].split(":")
            if len(start_parts) != 2 or len(stop_parts) != 2:
                raise ValueError("Invalid time format. Use HH:MM")
            start_h, start_m = int(start_parts[0]), int(start_parts[1])
            stop_h, stop_m = int(stop_parts[0]), int(stop_parts[1])
            if not (0 <= start_h <= 23 and 0 <= start_m <= 59):
                raise ValueError(f"Invalid start time: {e['start']}")
            if not (0 <= stop_h <= 24 and 0 <= stop_m <= 59):
                raise ValueError(f"Invalid stop time: {e['stop']}")
            entries.append((mode_map[e["mode"]], start_h, start_m, stop_h, stop_m))

        commands = build_schedule_commands(program, row, weekdays, entries)

        for coordinator in _get_coordinators(hass, device_id):
            await coordinator.client.set_schedule(commands)

    hass.services.async_register(
        DOMAIN, SERVICE_SET_MODE, handle_set_mode, schema=SERVICE_SET_MODE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_TEMPERATURE,
        handle_set_temperature,
        schema=SERVICE_SET_TEMPERATURE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_SCHEDULE,
        handle_get_schedule,
        schema=SERVICE_GET_SCHEDULE_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_SCHEDULE, handle_set_schedule, schema=SERVICE_SET_SCHEDULE_SCHEMA
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    hass.services.async_remove(DOMAIN, SERVICE_SET_MODE)
    hass.services.async_remove(DOMAIN, SERVICE_SET_TEMPERATURE)
    hass.services.async_remove(DOMAIN, SERVICE_GET_SCHEDULE)
    hass.services.async_remove(DOMAIN, SERVICE_SET_SCHEDULE)
