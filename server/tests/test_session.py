"""Tests for TD-02 (persist session): GET /me and POST /logout, and that
/login and /add_user actually establish a session on success.

Flask's test client (the `api` fixture) carries cookies across requests
within a test the same way a browser would -- a session cookie set by one
response is automatically sent on the next request from the same client.
"""


def _login(api, username, userId, password):
    return api.post("/login", json={"username": username, "userId": userId, "password": password})


def _add_user(api, username, userId, password):
    return api.post("/add_user", json={"username": username, "userId": userId, "password": password})


# ---------------------------------------------------------------------------
# GET /me with no prior sign-in
# ---------------------------------------------------------------------------


def test_me_returns_401_with_no_session(api):
    response = api.get("/me")
    assert response.status_code == 401
    assert response.get_json()["error"] == "not_signed_in"


# ---------------------------------------------------------------------------
# /login establishes a session GET /me can read back
# ---------------------------------------------------------------------------


def test_login_establishes_a_session(api):
    _add_user(api, "alice", "alice1", "correct horse battery")
    # /add_user itself already signs you in -- log out first so this test
    # isolates /login's own session-setting behavior.
    api.post("/logout")

    login_response = _login(api, "alice", "alice1", "correct horse battery")
    assert login_response.status_code == 200

    me_response = api.get("/me")
    assert me_response.status_code == 200
    assert me_response.get_json() == {"username": "alice", "userId": "alice1"}


def test_failed_login_does_not_establish_a_session(api):
    _add_user(api, "alice", "alice1", "correct horse battery")
    api.post("/logout")

    bad_login = _login(api, "alice", "alice1", "wrong password")
    assert bad_login.status_code == 401

    me_response = api.get("/me")
    assert me_response.status_code == 401


# ---------------------------------------------------------------------------
# /add_user also establishes a session (signing up signs you in)
# ---------------------------------------------------------------------------


def test_add_user_establishes_a_session(api):
    response = _add_user(api, "bob", "bob1", "correct horse battery")
    assert response.status_code == 201

    me_response = api.get("/me")
    assert me_response.status_code == 200
    assert me_response.get_json() == {"username": "bob", "userId": "bob1"}


# ---------------------------------------------------------------------------
# POST /logout clears the session
# ---------------------------------------------------------------------------


def test_logout_clears_the_session(api):
    _add_user(api, "alice", "alice1", "correct horse battery")
    assert api.get("/me").status_code == 200

    logout_response = api.post("/logout")
    assert logout_response.status_code == 200

    assert api.get("/me").status_code == 401


def test_logout_without_a_session_still_succeeds(api):
    # Calling logout when nothing was ever signed in should not error --
    # there's nothing to clear, which is not a failure case.
    response = api.post("/logout")
    assert response.status_code == 200
