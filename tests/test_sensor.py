from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from pykomfovent import KomfoventState

from custom_components.pykomfovent.const import DOMAIN
from custom_components.pykomfovent.sensor import SENSORS, async_setup_entry
from tests.conftest import make_add_entities


async def test_sensor_setup(hass: HomeAssistant, mock_state: KomfoventState) -> None:
    coordinator = MagicMock()
    coordinator.data = mock_state
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {
        "identifiers": {(DOMAIN, "192.168.0.137")},
        "name": "Komfovent (192.168.0.137)",
        "manufacturer": "Komfovent",
        "model": "C6",
    }

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    assert len(entities) == len(SENSORS)


async def test_sensor_values(hass: HomeAssistant, mock_state: KomfoventState) -> None:
    coordinator = MagicMock()
    coordinator.data = mock_state
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {
        "identifiers": {(DOMAIN, "192.168.0.137")},
        "name": "Komfovent (192.168.0.137)",
        "manufacturer": "Komfovent",
        "model": "C6",
    }

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    # Find specific sensors and check values
    mode_sensor = next(e for e in entities if e.entity_description.key == "mode")
    assert mode_sensor.native_value == "NORMALNY"

    supply_temp = next(e for e in entities if e.entity_description.key == "supply_temp")
    assert supply_temp.native_value == 21.5

    power = next(e for e in entities if e.entity_description.key == "power_consumption")
    assert power.native_value == 55.0


async def test_sensor_none_data(hass: HomeAssistant) -> None:
    coordinator = MagicMock()
    coordinator.data = None
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {
        "identifiers": {(DOMAIN, "192.168.0.137")},
        "name": "Komfovent (192.168.0.137)",
        "manufacturer": "Komfovent",
        "model": "C6",
    }

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    mode_sensor = next(e for e in entities if e.entity_description.key == "mode")
    assert mode_sensor.native_value is None


async def test_sensor_unique_ids(hass: HomeAssistant, mock_state: KomfoventState) -> None:
    coordinator = MagicMock()
    coordinator.data = mock_state
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    unique_ids = [e.unique_id for e in entities]
    assert len(unique_ids) == len(set(unique_ids))  # All unique
    assert "192.168.0.137_mode" in unique_ids
    assert "192.168.0.137_supply_temp" in unique_ids
