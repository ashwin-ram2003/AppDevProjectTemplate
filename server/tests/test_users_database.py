import pytest

import usersDatabase as usersDB
from passwordSecurity import InvalidPasswordError


# ---------------------------------------------------------------------------
# addUser
# ---------------------------------------------------------------------------


def test_add_user_stores_a_bcrypt_hash_not_the_plaintext(mongo):
    usersDB.addUser(mongo, "alice", "alice1", "correct horse battery")

    stored = mongo[usersDB.DB_NAME][usersDB.USERS_COLLECTION].find_one({"userId": "alice1"})
    assert stored["password"] != "correct horse battery"


def test_add_user_rejects_invalid_password(mongo):
    with pytest.raises(InvalidPasswordError):
        usersDB.addUser(mongo, "alice", "alice1", "short")


def test_add_user_rejects_duplicate_userId(mongo):
    usersDB.addUser(mongo, "alice", "alice1", "correct horse battery")
    with pytest.raises(usersDB.UserAlreadyExistsError):
        usersDB.addUser(mongo, "alice-again", "alice1", "another password")


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------


def test_login_succeeds_with_correct_credentials(mongo):
    usersDB.addUser(mongo, "alice", "alice1", "correct horse battery")
    assert usersDB.login(mongo, "alice", "alice1", "correct horse battery") is True


def test_login_fails_with_wrong_password(mongo):
    usersDB.addUser(mongo, "alice", "alice1", "correct horse battery")
    assert usersDB.login(mongo, "alice", "alice1", "wrong password") is False


def test_login_fails_for_unknown_user(mongo):
    assert usersDB.login(mongo, "nobody", "nobody1", "correct horse battery") is False
