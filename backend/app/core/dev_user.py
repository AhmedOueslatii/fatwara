import uuid

# Hardcoded dev user. Seeded by the initial alembic migration.
# Every persisted row uses this until PR 4 lands real auth (FastAPI-Users).
DEV_USER_ID: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000001")
