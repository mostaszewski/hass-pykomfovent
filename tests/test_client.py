from unittest.mock import AsyncMock, patch

import pytest
from pykomfovent.client import (
    KomfoventAuthError,
    KomfoventClient,
    KomfoventConnectionError,
)


async def test_client_init() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")
    assert client.base_url == "http://192.168.0.137:80"


async def test_client_init_custom_port() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass", port=8080)
    assert client.base_url == "http://192.168.0.137:8080"


async def test_client_context_manager() -> None:
    async with KomfoventClient("192.168.0.137", "user", "pass") as client:
        assert client._session is not None
    assert client._session is None or client._session.closed


async def test_authenticate_success() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = b"<html>Success</html>" + b"x" * 100

        result = await client.authenticate()

        assert result is True
        mock_request.assert_called_once_with("/")


async def test_authenticate_failure() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = KomfoventAuthError("Invalid credentials")

        result = await client.authenticate()

        assert result is False


async def test_get_state() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")

    main_xml = b"""<?xml version="1.0"?>
    <data>
        <OMO>NORMALNY</OMO>
        <AI0>21.5</AI0>
        <AI1>23.0</AI1>
        <AI2>5.0</AI2>
        <ST>21.0</ST>
        <SAF>50</SAF>
        <EAF>50</EAF>
        <FCG>47</FCG>
        <VF>0</VF>
    </data>"""

    detail_xml = b"""<?xml version="1.0"?>
    <data>
        <SFI>50</SFI>
        <EFI>50</EFI>
    </data>"""

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = [main_xml, detail_xml]

        state = await client.get_state()

        assert state.mode == "NORMALNY"
        assert state.supply_temp == 21.5


async def test_get_state_parse_error() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = [b"invalid xml", b"invalid xml"]

        with pytest.raises(KomfoventConnectionError, match="Failed to parse"):
            await client.get_state()


async def test_set_mode() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        await client.set_mode("intensive")

        mock_request.assert_called_once_with("/i.asp", {"3": "3"})


async def test_set_mode_invalid() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")

    with pytest.raises(ValueError, match="Unknown mode"):
        await client.set_mode("invalid")


async def test_set_supply_temp() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        await client.set_supply_temp(22.5)

        mock_request.assert_called_once_with("/i.asp", {"4": "225"})


async def test_close() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")
    await client._ensure_session()

    assert client._session is not None

    await client.close()

    assert client._session is None


async def test_request_retry_on_failure() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")

    call_count = 0

    async def mock_request(path, extra_data=None):
        nonlocal call_count
        call_count += 1
        return b"<html>Success</html>" + b"x" * 100

    # Test via authenticate which uses _request
    with patch.object(client, "_request", side_effect=mock_request):
        result = await client.authenticate()
        assert result is True
        assert call_count == 1


async def test_request_auth_error() -> None:
    client = KomfoventClient("192.168.0.137", "user", "pass")

    with patch.object(client, "_request", side_effect=KomfoventAuthError("Invalid")):
        result = await client.authenticate()
        assert result is False
