import hashlib
import secrets

TOKEN_BYTES = 32


def new_token() -> str:
    """A random token for a cookie. Only its hash is ever stored."""
    return secrets.token_urlsafe(TOKEN_BYTES)


def hash_token(token: str) -> bytes:
    """The hash that stands for the token in the database.

    The token is random and long, so a fast hash is enough: there is nothing to
    guess, unlike a password.
    """
    return hashlib.sha256(token.encode()).digest()
