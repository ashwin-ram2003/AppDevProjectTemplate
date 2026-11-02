"""Tests for POST /add_user and POST /login (US-01 Sign up, US-02 Sign in).

The hashing itself (passwordSecurity.py) and usersDatabase.addUser/login
have their own unit tests in test_password_security.py and
test_users_database.py. These tests cover the HTTP layer: how app.py's
routes translate usersDatabase's return values/exceptions into status
codes and JSON bodies, matching the pattern of the Track B hardware
routes (see test_request.py).
"""


def _add_user(api, username, userId, password):
    return api.post(
        "/add_user",
        json={"username": username, "userId": userId, "password": password},
    )


def _login(api, username, userId, password):
    return api.post(
        "/login",
        json={"username": username, "userId": userId, "password": password},
    )


# ---------------------------------------------------------------------------
# POST /add_user
# ---------------------------------------------------------------------------


def test_add_user_creates_account_and_returns_201(api):
    response = _add_user(api, "alice", "alice1", "correct horse battery")
    assert response.status_code == 201
    body = response.get_json()
    assert body == {"username": "alice", "userId": "alice1"}


def test_add_user_never_echoes_the_password(api):
    response = _add_user(api, "alice", "alice1", "correct horse battery")
    body = response.get_json()
    assert "password" not in body


def test_add_user_rejects_duplicate_userId(api):
    _add_user(api, "alice", "alice1", "correct horse battery")
    response = _add_user(api, "alice-again", "alice1", "a different password")
    assert response.status_code == 409


def test_add_user_rejects_short_password(api):
    response = _add_user(api, "alice", "alice1", "short")
    assert response.status_code == 400


def test_add_user_requires_username(api):
    response = api.post(
        "/add_user", json={"userId": "alice1", "password": "correct horse battery"}
    )
    assert response.status_code == 400
    assert response.get_json()["field"] == "username"


def test_add_user_requires_userId(api):
    response = api.post(
        "/add_user", json={"username": "alice", "password": "correct horse battery"}
    )
    assert response.status_code == 400
    assert response.get_json()["field"] == "userId"


def test_add_user_requires_password(api):
    response = api.post("/add_user", json={"username": "alice", "userId": "alice1"})
    assert response.status_code == 400
    assert response.get_json()["field"] == "password"


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------


def test_login_succeeds_with_correct_credentials(api):
    _add_user(api, "alice", "alice1", "correct horse battery")

    response = _login(api, "alice", "alice1", "correct horse battery")
    assert response.status_code == 200
    assert response.get_json() == {"username": "alice", "userId": "alice1"}


def test_login_rejects_wrong_password(api):
    _add_user(api, "alice", "alice1", "correct horse battery")

    response = _login(api, "alice", "alice1", "wrong password")
    assert response.status_code == 401


def test_login_rejects_unknown_user(api):
    response = _login(api, "nobody", "nobody1", "correct horse battery")
    assert response.status_code == 401


def test_login_unknown_user_and_wrong_password_give_the_same_error(api):
    """The response body must not let a caller distinguish "no such user"
    from "wrong password" -- that's how user enumeration happens."""
    _add_user(api, "alice", "alice1", "correct horse battery")

    wrongPassword = _login(api, "alice", "alice1", "wrong password")
    unknownUser = _login(api, "nobody", "nobody1", "correct horse battery")

    assert wrongPassword.status_code == unknownUser.status_code == 401
    assert wrongPassword.get_json() == unknownUser.get_json()


def test_login_requires_username(api):
    response = api.post(
        "/login", json={"userId": "alice1", "password": "correct horse battery"}
    )
    assert response.status_code == 400
    assert response.get_json()["field"] == "username"


def test_login_requires_password(api):
    response = api.post("/login", json={"username": "alice", "userId": "alice1"})
    assert response.status_code == 400
    assert response.get_json()["field"] == "password"
