import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pykomfovent import (
    KomfoventAuthError,
    KomfoventClient,
    KomfoventConnectionError,
    KomfoventState,
)

from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class KomfoventCoordinator(DataUpdateCoordinator[KomfoventState]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.client = KomfoventClient(
            entry.data[CONF_HOST],
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
        )
        self.host: str = entry.data[CONF_HOST]
        self._unavailable_logged = False

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.host)},
            name=f"Komfovent ({self.host})",
            manufacturer="Komfovent",
            model="C6",
        )

    async def _async_update_data(self) -> KomfoventState:
        try:
            data = await self.client.get_state()
            if self._unavailable_logged:
                _LOGGER.info("Connection to Komfovent %s restored", self.host)
                self._unavailable_logged = False
            return data
        except KomfoventAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except KomfoventConnectionError as err:
            if not self._unavailable_logged:
                _LOGGER.warning("Connection to Komfovent %s failed: %s", self.host, err)
                self._unavailable_logged = True
            raise UpdateFailed(f"Error communicating with device: {err}") from err
