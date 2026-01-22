from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from pykomfovent import KomfoventState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pykomfovent.const import DOMAIN
from custom_components.pykomfovent.diagnostics import async_get_config_entry_diagnostics


async def test_diagnostics(hass: HomeAssistant, mock_state: KomfoventState) -> None:
    coordinator = MagicMock()
    coordinator.data = mock_state
    coordinator.host = "192.168.0.137"

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Komfovent (192.168.0.137)",
        data={},
        entry_id="test_entry",
    )
    entry.add_to_hass(hass)

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert "config_entry" in result
    assert result["config_entry"]["entry_id"] == "test_entry"
    assert "device" in result
    assert result["device"]["host"] == "192.168.0.137"
    assert "state" in result
    assert result["state"]["mode"] == "NORMALNY"
    assert result["state"]["supply_temp"] == 21.5
    assert result["state"]["is_on"] is True
    assert result["state"]["flags_binary"] == "0b0"


async def test_diagnostics_no_data(hass: HomeAssistant) -> None:
    coordinator = MagicMock()
    coordinator.data = None

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Komfovent",
        data={},
        entry_id="test_entry",
    )
    entry.add_to_hass(hass)

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result == {"error": "No data available"}
