from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pykomfovent import KomfoventState

from .const import DOMAIN
from .coordinator import KomfoventCoordinator


@dataclass(frozen=True, kw_only=True)
class KomfoventNumberDescription(NumberEntityDescription):
    value_fn: Callable[[KomfoventState], float | None]
    set_fn: Callable[[KomfoventCoordinator, float], Coroutine[Any, Any, None]]


async def _set_supply_temp(coordinator: KomfoventCoordinator, value: float) -> None:
    await coordinator.client.set_supply_temp(value)
    await coordinator.async_request_refresh()


NUMBERS: tuple[KomfoventNumberDescription, ...] = (
    KomfoventNumberDescription(
        key="supply_temp_setpoint",
        translation_key="supply_temp_setpoint",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=10,
        native_max_value=30,
        native_step=0.5,
        mode=NumberMode.SLIDER,
        value_fn=lambda s: s.supply_temp_setpoint,
        set_fn=_set_supply_temp,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: KomfoventCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(KomfoventNumber(coordinator, description) for description in NUMBERS)
    # Also add mode config numbers
    from .mode_config import async_setup_numbers

    await async_setup_numbers(hass, entry, async_add_entities)


class KomfoventNumber(CoordinatorEntity[KomfoventCoordinator], NumberEntity):
    entity_description: KomfoventNumberDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KomfoventCoordinator,
        description: KomfoventNumberDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.host}_{description.key}"
        self._attr_translation_key = description.translation_key
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_set_native_value(self, value: float) -> None:
        await self.entity_description.set_fn(self.coordinator, value)
