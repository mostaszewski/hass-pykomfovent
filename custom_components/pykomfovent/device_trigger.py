import logging

import voluptuous as vol
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import state as state_trigger
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

TRIGGER_TYPES = {"filter_warning", "mode_changed"}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)


async def async_get_triggers(hass: HomeAssistant, device_id: str) -> list[dict]:
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)

    if not device or DOMAIN not in [i[0] for i in device.identifiers]:
        return []

    return [
        {
            CONF_PLATFORM: "device",
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: trigger_type,
        }
        for trigger_type in TRIGGER_TYPES
    ]


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    trigger_type = config[CONF_TYPE]
    device_id = config[CONF_DEVICE_ID]

    entity_registry = er.async_get(hass)
    entries = er.async_entries_for_device(entity_registry, device_id)

    if trigger_type == "filter_warning":
        entity_id = next(
            (
                e.entity_id
                for e in entries
                if "filter" in e.entity_id and "binary_sensor" in e.entity_id
            ),
            None,
        )
        if entity_id:
            state_config = {
                CONF_PLATFORM: "state",
                CONF_ENTITY_ID: entity_id,
                "to": "on",
            }
            return await state_trigger.async_attach_trigger(
                hass, state_config, action, trigger_info, platform_type="device"
            )

    elif trigger_type == "mode_changed":
        entity_id = next(
            (e.entity_id for e in entries if "mode" in e.entity_id and "select" in e.entity_id),
            None,
        )
        if entity_id:
            state_config = {
                CONF_PLATFORM: "state",
                CONF_ENTITY_ID: entity_id,
            }
            return await state_trigger.async_attach_trigger(
                hass, state_config, action, trigger_info, platform_type="device"
            )

    _LOGGER.warning(
        "Could not find entity for trigger type %s on device %s", trigger_type, device_id
    )
    return lambda: None
