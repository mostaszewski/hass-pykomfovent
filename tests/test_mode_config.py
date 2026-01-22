from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant

from custom_components.pykomfovent.const import DOMAIN
from custom_components.pykomfovent.mode_config import (
    MODE_NUMBERS,
    MODE_SWITCHES,
    ModeConfigNumber,
    ModeConfigSwitch,
    async_setup_numbers,
    async_setup_switches,
)


async def test_mode_config_numbers_setup(hass: HomeAssistant) -> None:
    coordinator = MagicMock()
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    await async_setup_numbers(hass, entry, lambda e: entities.extend(e))

    assert len(entities) == len(MODE_NUMBERS)
    assert all(isinstance(e, ModeConfigNumber) for e in entities)


async def test_mode_config_switches_setup(hass: HomeAssistant) -> None:
    coordinator = MagicMock()
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    await async_setup_switches(hass, entry, lambda e: entities.extend(e))

    assert len(entities) == len(MODE_SWITCHES)
    assert all(isinstance(e, ModeConfigSwitch) for e in entities)


async def test_mode_config_number_set(hass: HomeAssistant) -> None:
    coordinator = MagicMock()
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}
    coordinator.client = AsyncMock()

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    await async_setup_numbers(hass, entry, lambda e: entities.extend(e))

    # Test supply fan (no multiplier)
    fan_entity = next(e for e in entities if "supply_fan" in e.entity_description.key)
    fan_entity.async_write_ha_state = MagicMock()
    await fan_entity.async_set_native_value(50)
    coordinator.client.set_register.assert_called_with(fan_entity.entity_description.register, "50")

    # Test temperature (multiplier 10)
    temp_entity = next(e for e in entities if "_temp" in e.entity_description.key)
    temp_entity.async_write_ha_state = MagicMock()
    await temp_entity.async_set_native_value(21.5)
    coordinator.client.set_register.assert_called_with(
        temp_entity.entity_description.register, "215"
    )


async def test_mode_config_switch_toggle(hass: HomeAssistant) -> None:
    coordinator = MagicMock()
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}
    coordinator.client = AsyncMock()

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    await async_setup_switches(hass, entry, lambda e: entities.extend(e))

    switch = entities[0]
    switch.async_write_ha_state = MagicMock()

    await switch.async_turn_on()
    coordinator.client.set_register.assert_called_with(switch.entity_description.register, "on")
    assert switch.is_on is True

    await switch.async_turn_off()
    coordinator.client.set_register.assert_called_with(switch.entity_description.register, "0")
    assert switch.is_on is False
