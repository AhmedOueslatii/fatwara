import bcrypt

# bcrypt rejects passwords > 72 bytes outright (since 4.1). We truncate to match
# the historical bcrypt behavior so users with long passwords still register.
_MAX_BYTES = 72


def _truncate(plain: str) -> bytes:
    return plain.encode("utf-8")[:_MAX_BYTES]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_truncate(plain), bcrypt.gensalt()).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_truncate(plain), hashed.encode("ascii"))
    except ValueError:
        return False
