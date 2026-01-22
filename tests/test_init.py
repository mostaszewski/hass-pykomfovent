from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant
from pykomfovent import KomfoventState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pykomfovent.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DOMAIN,
)


async def test_setup_entry(
    hass: HomeAssistant, mock_state: KomfoventState, mock_client: AsyncMock
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Komfovent",
        data={
            CONF_HOST: "192.168.0.137",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
            CONF_SCAN_INTERVAL: 30,
        },
        entry_id="test_entry",
    )
    entry.add_to_hass(hass)

    # Mock hass.http
    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]


async def test_unload_entry(hass: HomeAssistant, mock_client: AsyncMock) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Komfovent",
        data={
            CONF_HOST: "192.168.0.137",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
            CONF_SCAN_INTERVAL: 30,
        },
        entry_id="test_entry",
    )
    entry.add_to_hass(hass)

    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.entry_id not in hass.data[DOMAIN]


async def test_unload_entry_keeps_services_with_other_entries(
    hass: HomeAssistant, mock_client: AsyncMock
) -> None:
    entry1 = MockConfigEntry(
        domain=DOMAIN,
        title="Komfovent 1",
        data={
            CONF_HOST: "192.168.0.137",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
            CONF_SCAN_INTERVAL: 30,
        },
        entry_id="test_entry_1",
    )
    entry1.add_to_hass(hass)

    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    await hass.config_entries.async_setup(entry1.entry_id)
    await hass.async_block_till_done()

    # Manually add a second coordinator to simulate multiple entries
    from custom_components.pykomfovent.coordinator import KomfoventCoordinator

    hass.data[DOMAIN]["fake_entry_2"] = MagicMock(spec=KomfoventCoordinator)

    # Verify services exist
    assert hass.services.has_service(DOMAIN, "set_mode")

    # Unload first entry - services should remain because fake_entry_2 exists
    await hass.config_entries.async_unload(entry1.entry_id)
    await hass.async_block_till_done()

    # Verify entry1 is unloaded but fake_entry_2 is still there
    assert entry1.entry_id not in hass.data[DOMAIN]
    assert "fake_entry_2" in hass.data[DOMAIN]
    # Services should still exist
    assert hass.services.has_service(DOMAIN, "set_mode")
