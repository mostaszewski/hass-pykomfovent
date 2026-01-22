import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
from pykomfovent.discovery import (
    KomfoventDiscovery,
    get_local_subnet,
)


def test_get_local_subnet() -> None:
    with patch("pykomfovent.discovery.socket.socket") as mock_socket:
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ("192.168.0.100", 12345)
        mock_sock.__enter__ = MagicMock(return_value=mock_sock)
        mock_sock.__exit__ = MagicMock(return_value=False)
        mock_socket.return_value = mock_sock

        result = get_local_subnet()

        assert result == "192.168.0.0/24"


def test_get_local_subnet_error() -> None:
    with patch("pykomfovent.discovery.socket.socket") as mock_socket:
        mock_sock = MagicMock()
        mock_sock.__enter__ = MagicMock(side_effect=OSError())
        mock_socket.return_value = mock_sock

        result = get_local_subnet()

        assert result is None


async def test_discovery_no_subnet() -> None:
    with patch(
        "pykomfovent.discovery.get_local_subnet",
        return_value=None,
    ):
        discovery = KomfoventDiscovery(subnet=None)

        result = await discovery.discover()

        assert result == []


async def test_check_host_found() -> None:
    discovery = KomfoventDiscovery(subnet="192.168.0.0/24")
    discovery._semaphore = asyncio.Semaphore(10)

    mock_response = MagicMock()
    mock_response.headers = {"Server": "C6"}
    mock_response.read = AsyncMock(return_value=b"<title>My Komfovent</title>")

    mock_session = MagicMock()
    mock_session.get = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock()
        )
    )

    result = await discovery._check_host(mock_session, "192.168.0.137")

    assert result is not None
    assert result.host == "192.168.0.137"
    assert result.name == "My Komfovent"


async def test_check_host_no_title() -> None:
    discovery = KomfoventDiscovery(subnet="192.168.0.0/24")
    discovery._semaphore = asyncio.Semaphore(10)

    mock_response = MagicMock()
    mock_response.headers = {"Server": "C6"}
    mock_response.read = AsyncMock(return_value=b"<html>no title</html>")

    mock_session = MagicMock()
    mock_session.get = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock()
        )
    )

    result = await discovery._check_host(mock_session, "192.168.0.1")

    assert result is not None
    assert result.name == "Komfovent"


async def test_check_host_wrong_server() -> None:
    discovery = KomfoventDiscovery(subnet="192.168.0.0/24")
    discovery._semaphore = asyncio.Semaphore(10)

    mock_response = MagicMock()
    mock_response.headers = {"Server": "Apache"}

    mock_session = MagicMock()
    mock_session.get = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock()
        )
    )

    result = await discovery._check_host(mock_session, "192.168.0.1")

    assert result is None


async def test_check_host_connection_error() -> None:
    discovery = KomfoventDiscovery(subnet="192.168.0.0/24")
    discovery._semaphore = asyncio.Semaphore(10)

    mock_session = MagicMock()
    mock_session.get = MagicMock(side_effect=aiohttp.ClientError())

    result = await discovery._check_host(mock_session, "192.168.0.1")

    assert result is None
