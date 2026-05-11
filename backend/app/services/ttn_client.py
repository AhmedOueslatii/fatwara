import asyncio
import random
import uuid
from dataclasses import dataclass
from typing import Literal, Protocol

from app.core.config import settings


TTNStatus = Literal["accepted", "rejected"]


@dataclass
class TTNResult:
    reference: str
    status: TTNStatus
    message: str | None = None


class TTNTimeout(RuntimeError):
    pass


class TTNError(RuntimeError):
    pass


class TTNClient(Protocol):
    async def submit(self, signed_xml: bytes) -> TTNResult: ...


class MockTTNClient:
    """In-memory TTN double. Mode controlled by settings.TTN_MOCK_MODE:

      - accept  (default): always returns accepted with a synthetic reference
      - reject:            always returns rejected with a synthetic reason
      - timeout:           always raises TTNTimeout (simulates network hang)
      - random:            70% accept, 20% reject, 10% timeout
    """

    def __init__(self, mode: str | None = None) -> None:
        self.mode = mode or settings.TTN_MOCK_MODE

    async def submit(self, signed_xml: bytes) -> TTNResult:
        await asyncio.sleep(0)  # yield, simulate I/O boundary

        mode = self.mode
        if mode == "random":
            roll = random.random()
            if roll < 0.7:
                mode = "accept"
            elif roll < 0.9:
                mode = "reject"
            else:
                mode = "timeout"

        if mode == "timeout":
            raise TTNTimeout("Mock TTN timeout")

        reference = f"TTN-MOCK-{uuid.uuid4().hex[:12].upper()}"

        if mode == "reject":
            return TTNResult(
                reference=reference,
                status="rejected",
                message="Mock rejection: invoice rejected by mock TTN",
            )

        if mode == "accept":
            return TTNResult(reference=reference, status="accepted")

        raise TTNError(f"Unknown TTN_MOCK_MODE: {mode}")


class RealTTNClient:
    """Skeleton for the eventual sandbox client. Not implemented until
    Ahmed has matricule + TunTrust cert + TTN partner registration."""

    async def submit(self, signed_xml: bytes) -> TTNResult:
        raise NotImplementedError(
            "Real TTN client not implemented yet. Set TTN_SANDBOX=true and use "
            "MockTTNClient until partner registration completes."
        )


def get_ttn_client() -> TTNClient:
    if settings.TTN_SANDBOX:
        return MockTTNClient()
    return RealTTNClient()
