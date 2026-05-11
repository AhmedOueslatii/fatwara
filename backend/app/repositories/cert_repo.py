import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.cert import Cert


class CertRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(
        self,
        *,
        user_id: uuid.UUID,
        storage_path: str,
        fmt: str,
        expires_at: datetime,
    ) -> Cert:
        existing = await self.get_by_user(user_id)
        if existing is not None:
            existing.storage_path = storage_path
            existing.format = fmt
            existing.expires_at = expires_at
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        cert = Cert(
            user_id=user_id,
            storage_path=storage_path,
            format=fmt,
            expires_at=expires_at,
        )
        self.session.add(cert)
        await self.session.commit()
        await self.session.refresh(cert)
        return cert

    async def get_by_user(self, user_id: uuid.UUID) -> Cert | None:
        result = await self.session.execute(
            select(Cert).where(Cert.user_id == user_id)
        )
        return result.scalar_one_or_none()
