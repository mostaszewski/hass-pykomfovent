from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant

from custom_components.pykomfovent.const import DOMAIN
from custom_components.pykomfovent.device_trigger import (
    TRIGGER_TYPES,
    async_attach_trigger,
    async_get_triggers,
)


async def test_get_triggers(hass: HomeAssistant) -> None:
    device = MagicMock()
    device.identifiers = {(DOMAIN, "192.168.0.137")}

    with patch("custom_components.pykomfovent.device_trigger.dr.async_get") as mock_dr:
        mock_dr.return_value.async_get.return_value = device

        triggers = await async_get_triggers(hass, "device_id")

        assert len(triggers) == len(TRIGGER_TYPES)
        trigger_types = {t["type"] for t in triggers}
        assert trigger_types == TRIGGER_TYPES


async def test_get_triggers_wrong_domain(hass: HomeAssistant) -> None:
    device = MagicMock()
    device.identifiers = {("other_domain", "192.168.0.137")}

    with patch("custom_components.pykomfovent.device_trigger.dr.async_get") as mock_dr:
        mock_dr.return_value.async_get.return_value = device

        triggers = await async_get_triggers(hass, "device_id")

        assert triggers == []


async def test_get_triggers_no_device(hass: HomeAssistant) -> None:
    with patch("custom_components.pykomfovent.device_trigger.dr.async_get") as mock_dr:
        mock_dr.return_value.async_get.return_value = None

        triggers = await async_get_triggers(hass, "device_id")

        assert triggers == []


async def test_attach_filter_warning_trigger(hass: HomeAssistant) -> None:
    entity = MagicMock()
    entity.entity_id = "binary_sensor.komfovent_filter_dirty"

    with (
        patch("custom_components.pykomfovent.device_trigger.er.async_get") as mock_er,
        patch(
            "custom_components.pykomfovent.device_trigger.state_trigger.async_attach_trigger"
        ) as mock_attach,
    ):
        mock_er.return_value = MagicMock()
        mock_er.return_value.__class__ = type(mock_er.return_value)

        with patch(
            "custom_components.pykomfovent.device_trigger.er.async_entries_for_device",
            return_value=[entity],
        ):
            config = {
                "platform": "device",
                "device_id": "device_id",
                "domain": DOMAIN,
                "type": "filter_warning",
            }

            mock_attach.return_value = AsyncMock()

            await async_attach_trigger(hass, config, AsyncMock(), MagicMock())

            mock_attach.assert_called_once()


async def test_attach_mode_changed_trigger(hass: HomeAssistant) -> None:
    entity = MagicMock()
    entity.entity_id = "select.komfovent_mode"

    with (
        patch("custom_components.pykomfovent.device_trigger.er.async_get") as mock_er,
        patch(
            "custom_components.pykomfovent.device_trigger.state_trigger.async_attach_trigger"
        ) as mock_attach,
    ):
        mock_er.return_value = MagicMock()

        with patch(
            "custom_components.pykomfovent.device_trigger.er.async_entries_for_device",
            return_value=[entity],
        ):
            config = {
                "platform": "device",
                "device_id": "device_id",
                "domain": DOMAIN,
                "type": "mode_changed",
            }

            mock_attach.return_value = AsyncMock()

            await async_attach_trigger(hass, config, AsyncMock(), MagicMock())

            mock_attach.assert_called_once()


async def test_attach_trigger_no_entity(hass: HomeAssistant) -> None:
    with (
        patch("custom_components.pykomfovent.device_trigger.er.async_get") as mock_er,
        patch(
            "custom_components.pykomfovent.device_trigger.er.async_entries_for_device",
            return_value=[],
        ),
    ):
        mock_er.return_value = MagicMock()

        config = {
            "platform": "device",
            "device_id": "device_id",
            "domain": DOMAIN,
            "type": "filter_warning",
        }

        result = await async_attach_trigger(hass, config, AsyncMock(), MagicMock())

        # Should return a no-op function
        assert callable(result)
