import os
import sys
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core import database  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def reset_db_between_tests():
    """Truncate invoice + audit_log between tests so persistence tests are isolated.

    Users table is left alone — the dev user seeded by alembic stays.

    Also disposes app.core.database.engine after each test, because pytest-asyncio
    creates a fresh event loop per test by default and asyncpg connections bound
    to a dead loop trigger "another operation is in progress" on reuse.
    """
    engine = create_async_engine(settings.DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE audit_log, invoices RESTART IDENTITY CASCADE"))
    await engine.dispose()
    yield
    await database.engine.dispose()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_invoice_payload():
    return {
        "supplier": {
            "name": "Cabinet Test",
            "matricule": "1234567A/P/M/000",
            "address": {
                "street_name": "Rue X",
                "city_name": "Tunis",
                "postal_zone": "1000",
                "country_subentity": "Tunis",
            },
        },
        "customer": {
            "name": "Client Test",
            "matricule": "9876543B/P/M/000",
            "address": {
                "street_name": "Rue Y",
                "city_name": "Sfax",
                "postal_zone": "3000",
                "country_subentity": "Sfax",
            },
        },
        "invoice_date": "2026-05-05",
        "items": [
            {
                "description": "Service",
                "quantity": "1",
                "unit_price": "100.000",
                "tva_rate": "19",
            }
        ],
    }
