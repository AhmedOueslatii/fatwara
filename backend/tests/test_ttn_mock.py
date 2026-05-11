import pytest

from app.services.ttn_client import MockTTNClient, TTNError, TTNTimeout


@pytest.mark.asyncio
async def test_mock_accept_mode():
    client = MockTTNClient(mode="accept")
    result = await client.submit(b"<signed/>")
    assert result.status == "accepted"
    assert result.reference.startswith("TTN-MOCK-")


@pytest.mark.asyncio
async def test_mock_reject_mode():
    client = MockTTNClient(mode="reject")
    result = await client.submit(b"<signed/>")
    assert result.status == "rejected"
    assert result.message is not None


@pytest.mark.asyncio
async def test_mock_timeout_mode():
    client = MockTTNClient(mode="timeout")
    with pytest.raises(TTNTimeout):
        await client.submit(b"<signed/>")


@pytest.mark.asyncio
async def test_mock_unknown_mode():
    client = MockTTNClient(mode="bogus")
    with pytest.raises(TTNError):
        await client.submit(b"<signed/>")
