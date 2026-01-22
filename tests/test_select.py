from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant
from pykomfovent import KomfoventState

from custom_components.pykomfovent.const import DOMAIN, MODES
from custom_components.pykomfovent.select import KomfoventModeSelect, async_setup_entry
from tests.conftest import make_add_entities


async def test_select_setup(hass: HomeAssistant, mock_state: KomfoventState) -> None:
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

    assert len(entities) == 1
    assert isinstance(entities[0], KomfoventModeSelect)


async def test_select_current_option(hass: HomeAssistant, mock_state: KomfoventState) -> None:
    coordinator = MagicMock()
    coordinator.data = mock_state  # mode = "NORMALNY"
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    select = entities[0]
    assert select.current_option == "normal"


async def test_select_set_option(hass: HomeAssistant, mock_state: KomfoventState) -> None:
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

    select = entities[0]
    await select.async_select_option("intensive")

    coordinator.client.set_mode.assert_called_once_with("intensive")
    coordinator.async_request_refresh.assert_called_once()


async def test_select_options(hass: HomeAssistant, mock_state: KomfoventState) -> None:
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

    select = entities[0]
    assert set(select.options) == set(MODES.keys())


async def test_select_none_data(hass: HomeAssistant) -> None:
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

    select = entities[0]
    assert select.current_option is None


async def test_select_unknown_mode(hass: HomeAssistant) -> None:
    coordinator = MagicMock()
    # Create state with unknown mode
    coordinator.data = MagicMock()
    coordinator.data.mode = "UNKNOWN_MODE"
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    select = entities[0]
    assert select.current_option is None
