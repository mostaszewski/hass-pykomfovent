from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant

from custom_components.pykomfovent.const import DOMAIN
from custom_components.pykomfovent.coordinator import KomfoventCoordinator
from custom_components.pykomfovent.services import async_setup_services, async_unload_services


async def test_setup_services(hass: HomeAssistant) -> None:
    await async_setup_services(hass)

    assert hass.services.has_service(DOMAIN, "set_mode")
    assert hass.services.has_service(DOMAIN, "set_temperature")
    assert hass.services.has_service(DOMAIN, "get_schedule")
    assert hass.services.has_service(DOMAIN, "set_schedule")


async def test_unload_services(hass: HomeAssistant) -> None:
    await async_setup_services(hass)
    await async_unload_services(hass)

    assert not hass.services.has_service(DOMAIN, "set_mode")
    assert not hass.services.has_service(DOMAIN, "set_temperature")
    assert not hass.services.has_service(DOMAIN, "get_schedule")
    assert not hass.services.has_service(DOMAIN, "set_schedule")


async def test_set_mode_service(hass: HomeAssistant) -> None:
    coordinator = MagicMock(spec=KomfoventCoordinator)
    coordinator.client = AsyncMock()
    coordinator.async_request_refresh = AsyncMock()

    hass.data[DOMAIN] = {"entry1": coordinator}

    await async_setup_services(hass)

    await hass.services.async_call(DOMAIN, "set_mode", {"mode": "intensive"}, blocking=True)

    coordinator.client.set_mode.assert_called_once_with("intensive")
    coordinator.async_request_refresh.assert_called_once()


async def test_set_temperature_service(hass: HomeAssistant) -> None:
    coordinator = MagicMock(spec=KomfoventCoordinator)
    coordinator.client = AsyncMock()
    coordinator.async_request_refresh = AsyncMock()

    hass.data[DOMAIN] = {"entry1": coordinator}

    await async_setup_services(hass)

    await hass.services.async_call(DOMAIN, "set_temperature", {"temperature": 22.5}, blocking=True)

    coordinator.client.set_supply_temp.assert_called_once_with(22.5)
    coordinator.async_request_refresh.assert_called_once()


async def test_get_schedule_service(hass: HomeAssistant) -> None:
    coordinator = MagicMock(spec=KomfoventCoordinator)
    coordinator.client = AsyncMock()
    coordinator.client.get_schedule = AsyncMock(
        return_value={
            "current_program": 0,
            "wmask": [127] + [0] * 15,
            "mode": [2] + [1] * 79,
            "start": [480] + [0] * 79,
            "stop": [1080] + [0] * 79,
        }
    )

    hass.data[DOMAIN] = {"entry1": coordinator}

    await async_setup_services(hass)

    result = await hass.services.async_call(
        DOMAIN, "get_schedule", {}, blocking=True, return_response=True
    )

    coordinator.client.get_schedule.assert_called_once()
    assert result["current_program"] == 0


async def test_set_schedule_service(hass: HomeAssistant) -> None:
    coordinator = MagicMock(spec=KomfoventCoordinator)
    coordinator.client = AsyncMock()
    coordinator.client.set_schedule = AsyncMock()

    hass.data[DOMAIN] = {"entry1": coordinator}

    await async_setup_services(hass)

    await hass.services.async_call(
        DOMAIN,
        "set_schedule",
        {
            "program": 0,
            "row": 0,
            "weekdays": 127,
            "entries": [
                {"mode": "normal", "start": "08:00", "stop": "18:00"},
            ],
        },
        blocking=True,
    )

    coordinator.client.set_schedule.assert_called_once()
    call_args = coordinator.client.set_schedule.call_args[0][0]
    assert call_args["700"] == 127
    assert call_args["620"] == 2  # normal
    assert call_args["300"] == 480  # 8*60
