from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pykomfovent import KomfoventState

from .const import DOMAIN, FILTER_WARNING_THRESHOLD
from .coordinator import KomfoventCoordinator


@dataclass(frozen=True, kw_only=True)
class KomfoventBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[KomfoventState], bool | None]


BINARY_SENSORS: tuple[KomfoventBinarySensorDescription, ...] = (
    KomfoventBinarySensorDescription(
        key="filter_dirty",
        translation_key="filter_dirty",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:air-filter",
        value_fn=lambda s: s.filter_contamination >= FILTER_WARNING_THRESHOLD
        if s.filter_contamination is not None
        else None,
    ),
    KomfoventBinarySensorDescription(
        key="heating_active",
        translation_key="heating_active",
        device_class=BinarySensorDeviceClass.HEAT,
        icon="mdi:heating-coil",
        value_fn=lambda s: s.heating_active,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: KomfoventCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(KomfoventBinarySensor(coordinator, desc) for desc in BINARY_SENSORS)


class KomfoventBinarySensor(CoordinatorEntity[KomfoventCoordinator], BinarySensorEntity):
    entity_description: KomfoventBinarySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KomfoventCoordinator,
        description: KomfoventBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.host}_{description.key}"
        self._attr_translation_key = description.translation_key
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
