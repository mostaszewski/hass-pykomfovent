import sys
from collections.abc import Callable, Generator
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from pykomfovent import KomfoventState

sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from custom_components.pykomfovent.const import CONF_SCAN_INTERVAL

pytest_plugins = "pytest_homeassistant_custom_component"


def make_add_entities(entities: list) -> Callable:
    def add_entities(new_entities: list) -> None:
        entities.extend(new_entities)

    return add_entities


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
def mock_state() -> KomfoventState:
    return KomfoventState(
        mode="NORMALNY",
        supply_temp=21.5,
        extract_temp=23.0,
        outdoor_temp=5.0,
        supply_temp_setpoint=21.0,
        extract_temp_setpoint=None,
        supply_fan_percent=50.0,
        extract_fan_percent=50.0,
        supply_fan_intensity=50.0,
        extract_fan_intensity=50.0,
        heat_exchanger_percent=10.0,
        electric_heater_percent=0.0,
        filter_contamination=47.0,
        heat_exchanger_efficiency=85.0,
        heat_recovery_power=300.0,
        power_consumption=55.0,
        heating_power=0.0,
        spi_actual=0.4,
        spi_daily=0.35,
        energy_consumed_daily=1.5,
        energy_consumed_monthly=40.0,
        energy_consumed_total=200.0,
        energy_heating_daily=0.0,
        energy_heating_monthly=0.0,
        energy_heating_total=0.0,
        energy_recovered_daily=5.0,
        energy_recovered_monthly=150.0,
        energy_recovered_total=1200.0,
        air_quality=22.0,
        humidity=45.0,
        flags=0,
    )


@pytest.fixture
def mock_client(mock_state: KomfoventState) -> Generator[AsyncMock]:
    with (
        patch("custom_components.pykomfovent.config_flow.KomfoventClient") as mock_client_class,
        patch("custom_components.pykomfovent.coordinator.KomfoventClient") as mock_coord_client,
    ):
        client = AsyncMock()
        client.authenticate = AsyncMock(return_value=True)
        client.get_state = AsyncMock(return_value=mock_state)
        client.set_mode = AsyncMock()
        client.set_supply_temp = AsyncMock()
        client.close = AsyncMock()

        mock_client_class.return_value = client
        mock_coord_client.return_value = client
        yield client


@pytest.fixture
def mock_discovery() -> Generator[AsyncMock]:
    with patch(
        "custom_components.pykomfovent.config_flow.KomfoventDiscovery"
    ) as mock_discovery_class:
        discovery = AsyncMock()
        discovery.discover = AsyncMock(return_value=[])
        mock_discovery_class.return_value = discovery
        yield discovery


@pytest.fixture
def config_entry_data() -> dict:
    return {
        CONF_HOST: "192.168.0.137",
        CONF_USERNAME: "user",
        CONF_PASSWORD: "pass",
        CONF_SCAN_INTERVAL: 30,
    }
