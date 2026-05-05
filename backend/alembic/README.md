# Alembic migrations

Schema migrations live in `versions/`. Empty for now — first migration ships in PR 2 (persistence layer).

```bash
# Generate a new migration after changing models
alembic revision --autogenerate -m "add users table"

# Apply migrations
alembic upgrade head

# Roll back one
alembic downgrade -1
```

`env.py` reads `DATABASE_URL` from `app.core.config.settings` so no separate alembic config needed.
