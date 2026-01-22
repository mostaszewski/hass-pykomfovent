from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from pykomfovent import KomfoventState

from custom_components.pykomfovent.binary_sensor import BINARY_SENSORS, async_setup_entry
from custom_components.pykomfovent.const import DOMAIN
from tests.conftest import make_add_entities


async def test_binary_sensor_setup(hass: HomeAssistant, mock_state: KomfoventState) -> None:
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

    assert len(entities) == len(BINARY_SENSORS)


async def test_filter_dirty_off(hass: HomeAssistant, mock_state: KomfoventState) -> None:
    coordinator = MagicMock()
    coordinator.data = mock_state  # filter_contamination = 47
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    filter_sensor = next(e for e in entities if e.entity_description.key == "filter_dirty")
    assert filter_sensor.is_on is False


async def test_filter_dirty_on(hass: HomeAssistant) -> None:
    state = KomfoventState(
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
        filter_contamination=85.0,  # Above threshold
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

    coordinator = MagicMock()
    coordinator.data = state
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    filter_sensor = next(e for e in entities if e.entity_description.key == "filter_dirty")
    assert filter_sensor.is_on is True


async def test_heating_active(hass: HomeAssistant) -> None:
    state = KomfoventState(
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
        electric_heater_percent=50.0,  # Heater active
        filter_contamination=47.0,
        heat_exchanger_efficiency=85.0,
        heat_recovery_power=300.0,
        power_consumption=55.0,
        heating_power=500.0,  # Heating power > 0
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

    coordinator = MagicMock()
    coordinator.data = state
    coordinator.host = "192.168.0.137"
    coordinator.device_info = {}

    entry = MagicMock()
    entry.entry_id = "test_entry"

    hass.data[DOMAIN] = {entry.entry_id: coordinator}

    entities = []
    async_add_entities = make_add_entities(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    heating_sensor = next(e for e in entities if e.entity_description.key == "heating_active")
    assert heating_sensor.is_on is True


async def test_binary_sensor_none_data(hass: HomeAssistant) -> None:
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

    filter_sensor = next(e for e in entities if e.entity_description.key == "filter_dirty")
    assert filter_sensor.is_on is None
