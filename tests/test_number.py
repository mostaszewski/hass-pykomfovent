from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant
from pykomfovent import KomfoventState

from custom_components.pykomfovent.const import DOMAIN
from custom_components.pykomfovent.mode_config import MODE_NUMBERS
from custom_components.pykomfovent.number import NUMBERS, KomfoventNumber, async_setup_entry
from tests.conftest import make_add_entities


async def test_number_setup(hass: HomeAssistant, mock_state: KomfoventState) -> None:
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

    # Main numbers + mode config numbers
    assert len(entities) == len(NUMBERS) + len(MODE_NUMBERS)


async def test_number_value(hass: HomeAssistant, mock_state: KomfoventState) -> None:
    coordinator = MagicMock()
    coordinator.data = mock_state  # supply_temp_setpoint = 21.0
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    # Find the main supply temp setpoint number
    number = next(e for e in entities if isinstance(e, KomfoventNumber))
    assert number.native_value == 21.0


async def test_number_set_value(hass: HomeAssistant, mock_state: KomfoventState) -> None:
    coordinator = MagicMock()
    coordinator.data = mock_state
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}
    coordinator.client = AsyncMock()
    coordinator.async_request_refresh = AsyncMock()

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    number = next(e for e in entities if isinstance(e, KomfoventNumber))
    await number.async_set_native_value(22.5)

    coordinator.client.set_supply_temp.assert_called_once_with(22.5)
    coordinator.async_request_refresh.assert_called_once()


async def test_number_none_data(hass: HomeAssistant) -> None:
    coordinator = MagicMock()
    coordinator.data = None
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    number = next(e for e in entities if isinstance(e, KomfoventNumber))
    assert number.native_value is None
