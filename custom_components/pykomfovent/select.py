from typing import ClassVar

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODES
from .coordinator import KomfoventCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: KomfoventCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KomfoventModeSelect(coordinator)])


class KomfoventModeSelect(CoordinatorEntity[KomfoventCoordinator], SelectEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "mode_select"
    _attr_icon = "mdi:hvac"
    _attr_options: ClassVar[list[str]] = list(MODES.keys())

    def __init__(self, coordinator: KomfoventCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_mode_select"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        mode = self.coordinator.data.mode.upper()
        for key, values in MODES.items():
            if mode in values:
                return key
        return None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.set_mode(option)
        await self.coordinator.async_request_refresh()
