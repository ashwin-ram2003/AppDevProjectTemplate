"""Password hashing and verification for user credentials (SR3).

Uses bcrypt -- a standard, one-way, salted password-hashing algorithm --
so plaintext passwords are never stored or compared directly. Each call to
hashPassword embeds a fresh random salt, so two users with the same
password get different stored hashes, and the same user hashing the same
password twice also gets different hashes.

This is independent of any homework cipher: bcrypt is a one-way hash (no
decrypt function exists, by design), whereas a cipher is reversible with
the right key. Passwords must never be recoverable, only verifiable.
"""

import bcrypt

# bcrypt's cost/work factor. Higher = slower to hash and verify, which is
# the point -- it makes brute-forcing leaked hashes more expensive. 12 is
# bcrypt's current recommended default (roughly 200-300ms per call on
# typical hardware).
_WORK_FACTOR = 12

# bcrypt only uses the first 72 bytes of the input and silently ignores
# the rest, which would let two different long passwords collide on the
# same hash. Reject anything over that limit instead of truncating.
_MAX_PASSWORD_BYTES = 72
_MIN_PASSWORD_LENGTH = 8


class InvalidPasswordError(ValueError):
    """Raised when a plaintext password fails validation before hashing."""


def _validatePassword(password):
    if not isinstance(password, str):
        raise InvalidPasswordError("password must be a string")
    if len(password) < _MIN_PASSWORD_LENGTH:
        raise InvalidPasswordError(
            f"password must be at least {_MIN_PASSWORD_LENGTH} characters"
        )
    if len(password.encode("utf-8")) > _MAX_PASSWORD_BYTES:
        raise InvalidPasswordError(
            f"password must be {_MAX_PASSWORD_BYTES} bytes or fewer"
        )


def hashPassword(password):
    """Hash a plaintext password for storage.

    Returns a str containing bcrypt's own encoding (algorithm identifier,
    cost, salt, and hash all together) -- safe to store as-is in Mongo and
    pass straight back into verifyPassword later.

    Raises InvalidPasswordError if the password fails basic validation.
    """
    _validatePassword(password)
    salt = bcrypt.gensalt(rounds=_WORK_FACTOR)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verifyPassword(password, storedHash):
    """Check a plaintext password attempt against a stored bcrypt hash.

    Returns True on match, False on any mismatch -- including a malformed
    or missing storedHash. Never raises, so a login route can call this
    directly on whatever it finds in the database.
    """
    if not isinstance(password, str) or not isinstance(storedHash, str):
        return False
    if not password or not storedHash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), storedHash.encode("utf-8"))
    except (ValueError, TypeError):
        # Malformed hash (corrupt/legacy data) -- treat as no-match rather
        # than crashing the caller.
        return False
