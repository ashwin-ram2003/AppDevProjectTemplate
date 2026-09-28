import pytest

from passwordSecurity import InvalidPasswordError, hashPassword, verifyPassword


# ---------------------------------------------------------------------------
# hashPassword -- validation
# ---------------------------------------------------------------------------


def test_hash_rejects_too_short_password():
    with pytest.raises(InvalidPasswordError):
        hashPassword("short1")


def test_hash_rejects_non_string():
    with pytest.raises(InvalidPasswordError):
        hashPassword(12345678)


def test_hash_rejects_password_over_72_bytes():
    with pytest.raises(InvalidPasswordError):
        hashPassword("x" * 73)


def test_hash_accepts_password_at_72_byte_boundary():
    # Should not raise.
    hashPassword("x" * 72)


# ---------------------------------------------------------------------------
# hashPassword -- output shape
# ---------------------------------------------------------------------------


def test_hash_output_is_not_the_plaintext():
    hashed = hashPassword("correct horse battery")
    assert hashed != "correct horse battery"


def test_hash_output_is_a_string():
    assert isinstance(hashPassword("correct horse battery"), str)


def test_same_password_hashed_twice_gives_different_hashes():
    # bcrypt salts each call independently.
    first = hashPassword("correct horse battery")
    second = hashPassword("correct horse battery")
    assert first != second


# ---------------------------------------------------------------------------
# verifyPassword -- matching behavior
# ---------------------------------------------------------------------------


def test_verify_accepts_correct_password():
    hashed = hashPassword("correct horse battery")
    assert verifyPassword("correct horse battery", hashed) is True


def test_verify_rejects_wrong_password():
    hashed = hashPassword("correct horse battery")
    assert verifyPassword("incorrect horse battery", hashed) is False


def test_verify_is_case_sensitive():
    hashed = hashPassword("correct horse battery")
    assert verifyPassword("Correct Horse Battery", hashed) is False


def test_two_different_hashes_of_same_password_both_verify():
    first = hashPassword("correct horse battery")
    second = hashPassword("correct horse battery")
    assert verifyPassword("correct horse battery", first) is True
    assert verifyPassword("correct horse battery", second) is True


# ---------------------------------------------------------------------------
# verifyPassword -- never raises, even on bad inputs
# ---------------------------------------------------------------------------


def test_verify_returns_false_for_malformed_hash():
    assert verifyPassword("correct horse battery", "not-a-real-bcrypt-hash") is False


def test_verify_returns_false_for_empty_password():
    hashed = hashPassword("correct horse battery")
    assert verifyPassword("", hashed) is False


def test_verify_returns_false_for_empty_stored_hash():
    assert verifyPassword("correct horse battery", "") is False


def test_verify_returns_false_for_non_string_password():
    hashed = hashPassword("correct horse battery")
    assert verifyPassword(12345678, hashed) is False
