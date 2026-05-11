import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.audit_log import AuditLog


class AuditRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log(
        self,
        *,
        user_id: uuid.UUID,
        action: str,
        invoice_id: uuid.UUID | None = None,
        detail: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            invoice_id=invoice_id,
            detail=detail,
        )
        self.session.add(entry)
        await self.session.commit()
        return entry
