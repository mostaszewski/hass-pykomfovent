from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pykomfovent import (
    KomfoventAuthError,
    KomfoventConnectionError,
)

from custom_components.pykomfovent.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DOMAIN,
)


async def test_form_user_manual(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "192.168.0.137",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
            CONF_SCAN_INTERVAL: 30,
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Komfovent (192.168.0.137)"
    assert result["data"][CONF_HOST] == "192.168.0.137"


async def test_form_autodiscovery(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    mock_device = MagicMock()
    mock_device.host = "192.168.0.100"
    mock_device.name = "Komfovent"
    mock_discovery.discover.return_value = [mock_device]

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HOST] == "192.168.0.100"


async def test_form_autodiscovery_skips_configured(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    # Add existing entry
    existing = MockConfigEntry(
        domain=DOMAIN,
        title="Komfovent",
        data={CONF_HOST: "192.168.0.100", CONF_USERNAME: "user", CONF_PASSWORD: "pass"},
        unique_id="192.168.0.100",
    )
    existing.add_to_hass(hass)

    # Discovery returns two devices, first is already configured
    mock_device1 = MagicMock()
    mock_device1.host = "192.168.0.100"  # Already configured
    mock_device2 = MagicMock()
    mock_device2.host = "192.168.0.101"  # New device
    mock_discovery.discover.return_value = [mock_device1, mock_device2]

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HOST] == "192.168.0.101"  # Should use second device


async def test_form_discovery_failed(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    mock_discovery.discover.return_value = []

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "discovery_failed"


async def test_form_cannot_connect(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    mock_client.authenticate.side_effect = KomfoventConnectionError("Connection failed")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "192.168.0.137",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


async def test_form_invalid_auth(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    mock_client.authenticate.return_value = False

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "192.168.0.137",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "wrong",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"


async def test_form_auth_error_exception(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    mock_client.authenticate.side_effect = KomfoventAuthError("Auth failed")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "192.168.0.137",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"


async def test_form_already_configured(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    # Create a real config entry with unique_id
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Komfovent",
        data={CONF_HOST: "192.168.0.137", CONF_USERNAME: "user", CONF_PASSWORD: "pass"},
        entry_id="test_entry",
        unique_id="192.168.0.137",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "192.168.0.137",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
        },
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauth_flow(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_HOST: "192.168.0.137",
        CONF_USERNAME: "old_user",
        CONF_PASSWORD: "old_pass",
    }

    with patch.object(hass.config_entries, "async_get_entry", return_value=entry):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_REAUTH, "entry_id": "test_entry_id"},
            data=entry.data,
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "reauth_confirm"


async def test_reauth_flow_confirm(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Komfovent",
        data={
            CONF_HOST: "192.168.0.137",
            CONF_USERNAME: "old_user",
            CONF_PASSWORD: "old_pass",
        },
        entry_id="test_entry_id",
        unique_id="192.168.0.137",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_REAUTH, "entry_id": entry.entry_id},
        data=entry.data,
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_USERNAME: "new_user", CONF_PASSWORD: "new_pass"},
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"


async def test_reauth_flow_invalid_auth(
    hass: HomeAssistant, mock_client: AsyncMock, mock_discovery: AsyncMock
) -> None:
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    mock_client.authenticate.return_value = False

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Komfovent",
        data={
            CONF_HOST: "192.168.0.137",
            CONF_USERNAME: "old_user",
            CONF_PASSWORD: "old_pass",
        },
        entry_id="test_entry_id",
        unique_id="192.168.0.137",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_REAUTH, "entry_id": entry.entry_id},
        data=entry.data,
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_USERNAME: "new_user", CONF_PASSWORD: "wrong_pass"},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"


async def test_options_flow(hass: HomeAssistant, mock_client: AsyncMock) -> None:
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_HOST: "192.168.0.137",
        CONF_USERNAME: "user",
        CONF_PASSWORD: "pass",
        CONF_SCAN_INTERVAL: 30,
    }

    with (
        patch.object(hass.config_entries, "async_get_entry", return_value=entry),
        patch.object(hass.config_entries, "async_update_entry"),
        patch.object(hass.config_entries, "async_reload", return_value=True),
    ):
        from custom_components.pykomfovent.config_flow import KomfoventOptionsFlow

        flow = KomfoventOptionsFlow(entry)
        flow.hass = hass

        result = await flow.async_step_init()
        assert result["type"] == FlowResultType.FORM

        result = await flow.async_step_init({CONF_SCAN_INTERVAL: 60})
        assert result["type"] == FlowResultType.CREATE_ENTRY


async def test_get_options_flow(hass: HomeAssistant) -> None:
    from custom_components.pykomfovent.config_flow import KomfoventConfigFlow, KomfoventOptionsFlow

    entry = MagicMock()
    options_flow = KomfoventConfigFlow.async_get_options_flow(entry)

    assert isinstance(options_flow, KomfoventOptionsFlow)
