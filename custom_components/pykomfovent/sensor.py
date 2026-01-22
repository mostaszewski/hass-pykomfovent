from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pykomfovent import KomfoventState

from .const import DOMAIN
from .coordinator import KomfoventCoordinator


@dataclass(frozen=True, kw_only=True)
class KomfoventSensorDescription(SensorEntityDescription):
    value_fn: Callable[[KomfoventState], float | str | None]


SENSORS: tuple[KomfoventSensorDescription, ...] = (
    KomfoventSensorDescription(
        key="mode",
        translation_key="mode",
        icon="mdi:hvac",
        value_fn=lambda s: s.mode,
    ),
    KomfoventSensorDescription(
        key="supply_temp",
        translation_key="supply_temp",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda s: s.supply_temp,
    ),
    KomfoventSensorDescription(
        key="extract_temp",
        translation_key="extract_temp",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda s: s.extract_temp,
    ),
    KomfoventSensorDescription(
        key="outdoor_temp",
        translation_key="outdoor_temp",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda s: s.outdoor_temp,
    ),
    KomfoventSensorDescription(
        key="supply_fan",
        translation_key="supply_fan",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.supply_fan_percent,
    ),
    KomfoventSensorDescription(
        key="extract_fan",
        translation_key="extract_fan",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.extract_fan_percent,
    ),
    KomfoventSensorDescription(
        key="supply_fan_intensity",
        translation_key="supply_fan_intensity",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.supply_fan_intensity,
    ),
    KomfoventSensorDescription(
        key="extract_fan_intensity",
        translation_key="extract_fan_intensity",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.extract_fan_intensity,
    ),
    KomfoventSensorDescription(
        key="filter_contamination",
        translation_key="filter_contamination",
        icon="mdi:air-filter",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.filter_contamination,
    ),
    KomfoventSensorDescription(
        key="heat_exchanger_percent",
        translation_key="heat_exchanger_percent",
        icon="mdi:heat-wave",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.heat_exchanger_percent,
    ),
    KomfoventSensorDescription(
        key="heat_exchanger_efficiency",
        translation_key="heat_exchanger_efficiency",
        icon="mdi:heat-wave",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.heat_exchanger_efficiency,
    ),
    KomfoventSensorDescription(
        key="electric_heater_percent",
        translation_key="electric_heater_percent",
        icon="mdi:heating-coil",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.electric_heater_percent,
    ),
    KomfoventSensorDescription(
        key="heat_recovery_power",
        translation_key="heat_recovery_power",
        icon="mdi:heat-wave",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.heat_recovery_power,
    ),
    KomfoventSensorDescription(
        key="power_consumption",
        translation_key="power_consumption",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.power_consumption,
    ),
    KomfoventSensorDescription(
        key="heating_power",
        translation_key="heating_power",
        icon="mdi:heating-coil",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.heating_power,
    ),
    KomfoventSensorDescription(
        key="spi_actual",
        translation_key="spi_actual",
        icon="mdi:speedometer",
        native_unit_of_measurement="W/(m³/h)",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.spi_actual,
    ),
    KomfoventSensorDescription(
        key="spi_daily",
        translation_key="spi_daily",
        icon="mdi:speedometer",
        native_unit_of_measurement="W/(m³/h)",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.spi_daily,
    ),
    KomfoventSensorDescription(
        key="energy_consumed_daily",
        translation_key="energy_consumed_daily",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda s: s.energy_consumed_daily,
    ),
    KomfoventSensorDescription(
        key="energy_consumed_monthly",
        translation_key="energy_consumed_monthly",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda s: s.energy_consumed_monthly,
    ),
    KomfoventSensorDescription(
        key="energy_consumed_total",
        translation_key="energy_consumed_total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda s: s.energy_consumed_total,
    ),
    KomfoventSensorDescription(
        key="energy_heating_daily",
        translation_key="energy_heating_daily",
        icon="mdi:heating-coil",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda s: s.energy_heating_daily,
    ),
    KomfoventSensorDescription(
        key="energy_heating_monthly",
        translation_key="energy_heating_monthly",
        icon="mdi:heating-coil",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda s: s.energy_heating_monthly,
    ),
    KomfoventSensorDescription(
        key="energy_heating_total",
        translation_key="energy_heating_total",
        icon="mdi:heating-coil",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda s: s.energy_heating_total,
    ),
    KomfoventSensorDescription(
        key="energy_recovered_daily",
        translation_key="energy_recovered_daily",
        icon="mdi:leaf",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda s: s.energy_recovered_daily,
    ),
    KomfoventSensorDescription(
        key="energy_recovered_monthly",
        translation_key="energy_recovered_monthly",
        icon="mdi:leaf",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda s: s.energy_recovered_monthly,
    ),
    KomfoventSensorDescription(
        key="energy_recovered_total",
        translation_key="energy_recovered_total",
        icon="mdi:leaf",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda s: s.energy_recovered_total,
    ),
    KomfoventSensorDescription(
        key="air_quality",
        translation_key="air_quality",
        icon="mdi:air-purifier",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.air_quality,
    ),
    KomfoventSensorDescription(
        key="humidity",
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.humidity,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: KomfoventCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(KomfoventSensor(coordinator, description) for description in SENSORS)


class KomfoventSensor(CoordinatorEntity[KomfoventCoordinator], SensorEntity):
    entity_description: KomfoventSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KomfoventCoordinator,
        description: KomfoventSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.host}_{description.key}"
        self._attr_translation_key = description.translation_key
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | str | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
