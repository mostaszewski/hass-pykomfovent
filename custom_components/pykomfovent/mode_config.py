from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import KomfoventCoordinator

MODES = ["away", "normal", "intensive", "boost", "hood", "fireplace", "override", "vacation"]

# Register mappings from Komfovent C6 web interface (c_cfg.html, c_cfg2.html)
MODE_SUPPLY_FAN = {0: 247, 1: 248, 2: 249, 3: 250, 4: 251, 5: 252, 6: 253}  # No vacation
MODE_EXTRACT_FAN = {0: 255, 1: 256, 2: 257, 3: 258, 4: 259, 5: 260, 6: 261}
MODE_TEMP = {0: 263, 1: 264, 2: 265, 3: 266, 4: 267, 5: 268, 6: 269, 7: 270}
MODE_HUMIDITY = {0: 816, 1: 817, 2: 818, 3: 819}  # Only first 4 modes
MODE_HEATER = {0: 271, 1: 272, 2: 273, 3: 274, 4: 275, 5: 276, 6: 277, 7: 278}

# ECO settings from c_cfg2.html
ECO_MIN_TEMP = 245
ECO_MAX_TEMP = 246
ECO_FREE_COOLING = 242
ECO_BLOCK_HEATER = 243
ECO_BLOCK_COOLER = 244
ECO_HEAT_RECOVERY = 847

# AUTO settings
AUTO_TEMP = 232  # Already handled in number.py
AUTO_AIR_QUALITY = 233
AUTO_HUMIDITY = 234
AUTO_HEATER = 240


@dataclass(frozen=True, kw_only=True)
class ModeConfigNumberDescription(NumberEntityDescription):
    register: int
    multiplier: float = 1.0
    entity_registry_enabled_default: bool = True


@dataclass(frozen=True, kw_only=True)
class ModeConfigSwitchDescription(SwitchEntityDescription):
    register: int
    entity_registry_enabled_default: bool = True


def _build_mode_numbers() -> list[ModeConfigNumberDescription]:
    numbers: list[ModeConfigNumberDescription] = []

    # Supply fan % per mode (not vacation)
    for i, mode in enumerate(MODES[:7]):
        numbers.append(
            ModeConfigNumberDescription(
                key=f"mode_{mode}_supply_fan",
                translation_key=f"mode_{mode}_supply_fan",
                icon="mdi:fan",
                native_unit_of_measurement=PERCENTAGE,
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                mode=NumberMode.SLIDER,
                register=MODE_SUPPLY_FAN[i],
            )
        )

    # Extract fan % per mode (not vacation)
    for i, mode in enumerate(MODES[:7]):
        numbers.append(
            ModeConfigNumberDescription(
                key=f"mode_{mode}_extract_fan",
                translation_key=f"mode_{mode}_extract_fan",
                icon="mdi:fan",
                native_unit_of_measurement=PERCENTAGE,
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                mode=NumberMode.SLIDER,
                register=MODE_EXTRACT_FAN[i],
            )
        )

    # Temperature per mode (all modes)
    for i, mode in enumerate(MODES):
        numbers.append(
            ModeConfigNumberDescription(
                key=f"mode_{mode}_temp",
                translation_key=f"mode_{mode}_temp",
                icon="mdi:thermometer",
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                native_min_value=10,
                native_max_value=30,
                native_step=0.5,
                mode=NumberMode.SLIDER,
                register=MODE_TEMP[i],
                multiplier=10.0,
            )
        )

    # Humidity per mode (first 4 modes only)
    for i, mode in enumerate(MODES[:4]):
        numbers.append(
            ModeConfigNumberDescription(
                key=f"mode_{mode}_humidity",
                translation_key=f"mode_{mode}_humidity",
                icon="mdi:water-percent",
                native_unit_of_measurement=PERCENTAGE,
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                mode=NumberMode.SLIDER,
                register=MODE_HUMIDITY[i],
            )
        )

    # ECO settings
    numbers.extend(
        [
            ModeConfigNumberDescription(
                key="eco_min_supply_temp",
                translation_key="eco_min_supply_temp",
                icon="mdi:thermometer-low",
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                native_min_value=5,
                native_max_value=25,
                native_step=0.5,
                mode=NumberMode.SLIDER,
                register=ECO_MIN_TEMP,
                multiplier=10.0,
            ),
            ModeConfigNumberDescription(
                key="eco_max_supply_temp",
                translation_key="eco_max_supply_temp",
                icon="mdi:thermometer-high",
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                native_min_value=15,
                native_max_value=35,
                native_step=0.5,
                mode=NumberMode.SLIDER,
                register=ECO_MAX_TEMP,
                multiplier=10.0,
            ),
        ]
    )

    # AUTO settings (temp already in number.py)
    numbers.extend(
        [
            ModeConfigNumberDescription(
                key="auto_air_quality",
                translation_key="auto_air_quality",
                icon="mdi:air-filter",
                native_unit_of_measurement=PERCENTAGE,
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                mode=NumberMode.SLIDER,
                register=AUTO_AIR_QUALITY,
            ),
            ModeConfigNumberDescription(
                key="auto_humidity",
                translation_key="auto_humidity",
                icon="mdi:water-percent",
                native_unit_of_measurement=PERCENTAGE,
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                mode=NumberMode.SLIDER,
                register=AUTO_HUMIDITY,
            ),
        ]
    )

    return numbers


def _build_mode_switches() -> list[ModeConfigSwitchDescription]:
    switches: list[ModeConfigSwitchDescription] = []

    # Electric heater per mode
    for i, mode in enumerate(MODES):
        switches.append(
            ModeConfigSwitchDescription(
                key=f"mode_{mode}_heater",
                translation_key=f"mode_{mode}_heater",
                icon="mdi:radiator",
                register=MODE_HEATER[i],
            )
        )

    # ECO switches
    switches.extend(
        [
            ModeConfigSwitchDescription(
                key="eco_free_cooling",
                translation_key="eco_free_cooling",
                icon="mdi:snowflake",
                register=ECO_FREE_COOLING,
            ),
            ModeConfigSwitchDescription(
                key="eco_block_heater",
                translation_key="eco_block_heater",
                icon="mdi:radiator-off",
                register=ECO_BLOCK_HEATER,
            ),
            ModeConfigSwitchDescription(
                key="eco_block_cooler",
                translation_key="eco_block_cooler",
                icon="mdi:snowflake-off",
                register=ECO_BLOCK_COOLER,
            ),
            ModeConfigSwitchDescription(
                key="auto_heater",
                translation_key="auto_heater",
                icon="mdi:radiator",
                register=AUTO_HEATER,
            ),
        ]
    )

    return switches


MODE_NUMBERS = _build_mode_numbers()
MODE_SWITCHES = _build_mode_switches()


class ModeConfigNumber(CoordinatorEntity[KomfoventCoordinator], NumberEntity):
    entity_description: ModeConfigNumberDescription
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, coordinator: KomfoventCoordinator, description: ModeConfigNumberDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.host}_{description.key}"
        self._attr_translation_key = description.translation_key
        self._attr_device_info = coordinator.device_info
        self._value: float | None = None

    @property
    def native_value(self) -> float | None:
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        reg = self.entity_description.register
        mult = self.entity_description.multiplier
        await self.coordinator.client.set_register(reg, str(int(value * mult)))
        self._value = value
        self.async_write_ha_state()


class ModeConfigSwitch(CoordinatorEntity[KomfoventCoordinator], SwitchEntity):
    entity_description: ModeConfigSwitchDescription
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, coordinator: KomfoventCoordinator, description: ModeConfigSwitchDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.host}_{description.key}"
        self._attr_translation_key = description.translation_key
        self._attr_device_info = coordinator.device_info
        self._is_on: bool | None = None

    @property
    def is_on(self) -> bool | None:
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.client.set_register(self.entity_description.register, "on")
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        # HTML checkboxes: unchecked = not sent. Send "0" to explicitly disable.
        await self.coordinator.client.set_register(self.entity_description.register, "0")
        self._is_on = False
        self.async_write_ha_state()


async def async_setup_numbers(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: KomfoventCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ModeConfigNumber(coordinator, desc) for desc in MODE_NUMBERS)


async def async_setup_switches(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: KomfoventCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ModeConfigSwitch(coordinator, desc) for desc in MODE_SWITCHES)
