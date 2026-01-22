from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pykomfovent import (
    KomfoventAuthError,
    KomfoventConnectionError,
    KomfoventState,
)

from custom_components.pykomfovent.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DOMAIN,
)
from custom_components.pykomfovent.coordinator import KomfoventCoordinator


async def test_coordinator_update_success(hass: HomeAssistant, mock_state: KomfoventState) -> None:
    entry = MagicMock()
    entry.data = {
        CONF_HOST: "192.168.0.137",
        CONF_USERNAME: "user",
        CONF_PASSWORD: "pass",
        CONF_SCAN_INTERVAL: 30,
    }

    with patch("custom_components.pykomfovent.coordinator.KomfoventClient") as mock_client_class:
        client = AsyncMock()
        client.get_state = AsyncMock(return_value=mock_state)
        mock_client_class.return_value = client

        coordinator = KomfoventCoordinator(hass, entry)
        data = await coordinator._async_update_data()

        assert data.mode == "NORMALNY"
        assert data.supply_temp == 21.5


async def test_coordinator_update_connection_error(hass: HomeAssistant) -> None:
    entry = MagicMock()
    entry.data = {
        CONF_HOST: "192.168.0.137",
        CONF_USERNAME: "user",
        CONF_PASSWORD: "pass",
        CONF_SCAN_INTERVAL: 30,
    }

    with patch("custom_components.pykomfovent.coordinator.KomfoventClient") as mock_client_class:
        client = AsyncMock()
        client.get_state = AsyncMock(side_effect=KomfoventConnectionError("Connection failed"))
        mock_client_class.return_value = client

        coordinator = KomfoventCoordinator(hass, entry)

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


async def test_coordinator_update_auth_error(hass: HomeAssistant) -> None:
    entry = MagicMock()
    entry.data = {
        CONF_HOST: "192.168.0.137",
        CONF_USERNAME: "user",
        CONF_PASSWORD: "pass",
        CONF_SCAN_INTERVAL: 30,
    }

    with patch("custom_components.pykomfovent.coordinator.KomfoventClient") as mock_client_class:
        client = AsyncMock()
        client.get_state = AsyncMock(side_effect=KomfoventAuthError("Auth failed"))
        mock_client_class.return_value = client

        coordinator = KomfoventCoordinator(hass, entry)

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


async def test_coordinator_device_info(hass: HomeAssistant) -> None:
    entry = MagicMock()
    entry.data = {
        CONF_HOST: "192.168.0.137",
        CONF_USERNAME: "user",
        CONF_PASSWORD: "pass",
        CONF_SCAN_INTERVAL: 30,
    }

    with patch("custom_components.pykomfovent.coordinator.KomfoventClient"):
        coordinator = KomfoventCoordinator(hass, entry)
        device_info = coordinator.device_info

        assert device_info["identifiers"] == {(DOMAIN, "192.168.0.137")}
        assert device_info["manufacturer"] == "Komfovent"
        assert device_info["model"] == "C6"


async def test_coordinator_unavailable_logging(hass: HomeAssistant) -> None:
    entry = MagicMock()
    entry.data = {
        CONF_HOST: "192.168.0.137",
        CONF_USERNAME: "user",
        CONF_PASSWORD: "pass",
        CONF_SCAN_INTERVAL: 30,
    }

    with patch("custom_components.pykomfovent.coordinator.KomfoventClient") as mock_client_class:
        client = AsyncMock()
        client.get_state = AsyncMock(side_effect=KomfoventConnectionError("Connection failed"))
        mock_client_class.return_value = client

        coordinator = KomfoventCoordinator(hass, entry)

        # First failure
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
        assert coordinator._unavailable_logged is True

        # Second failure - should not log again
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
        assert coordinator._unavailable_logged is True


async def test_coordinator_connection_restored(
    hass: HomeAssistant, mock_state: KomfoventState
) -> None:
    entry = MagicMock()
    entry.data = {
        CONF_HOST: "192.168.0.137",
        CONF_USERNAME: "user",
        CONF_PASSWORD: "pass",
        CONF_SCAN_INTERVAL: 30,
    }

    with patch("custom_components.pykomfovent.coordinator.KomfoventClient") as mock_client_class:
        client = AsyncMock()
        mock_client_class.return_value = client

        coordinator = KomfoventCoordinator(hass, entry)
        coordinator._unavailable_logged = True

        # Connection restored
        client.get_state = AsyncMock(return_value=mock_state)
        data = await coordinator._async_update_data()

        assert coordinator._unavailable_logged is False
        assert data.mode == "NORMALNY"
