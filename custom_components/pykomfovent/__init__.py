import contextlib

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import KomfoventCoordinator
from .services import async_setup_services, async_unload_services

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = KomfoventCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    if len(hass.data[DOMAIN]) == 1:
        await async_setup_services(hass)
        card_path = hass.config.path("custom_components/pykomfovent/www/komfovent-card.js")
        with contextlib.suppress(RuntimeError):
            await hass.http.async_register_static_paths(
                [StaticPathConfig("/komfovent/komfovent-card.js", card_path, True)]
            )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: KomfoventCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.close()

        if not hass.data[DOMAIN]:
            await async_unload_services(hass)

    return unload_ok
