import os
import sys

# Use the in-memory fake MongoDB and skip seeding hardware sets.
# These must be set BEFORE importing app, since app.py reads them at import time.
os.environ["USE_MOCK_DB"] = "1"
os.environ["SKIP_SEED"] = "1"

# Let this file import app.py and the other server modules from the folder above
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

import app as server
from encryption import protect_user_id

VALID_USER = {"username": "Jane", "userId": "jane123", "password": "secret"}


@pytest.fixture
def client():
    # Start every test with an empty database
    server.client.drop_database("HardwareCheckout")
    server.app.config["TESTING"] = True
    with server.app.test_client() as c:
        yield c


def add_user(c, **overrides):
    payload = {**VALID_USER, **overrides}
    return c.post("/add_user", json=payload)


def test_create_user_success(client):
    res = add_user(client)
    body = res.get_json()

    assert res.status_code == 201
    assert body["success"] is True
    assert body["userId"] == "jane123"
    assert body["username"] == "Jane"


def test_user_is_stored_with_hashed_id_and_password(client):
    add_user(client)
    users = server.client["HardwareCheckout"]["Users"]

    # The raw userId should never be stored
    assert users.find_one({"userId": "jane123"}) is None

    doc = users.find_one({"userId": protect_user_id("jane123")})
    assert doc is not None
    assert doc["password"] != "secret"
    assert doc["projects"] == []


def test_duplicate_user_id_rejected(client):
    add_user(client)
    res = add_user(client, username="Someone Else")

    assert res.status_code == 409
    assert res.get_json()["success"] is False


@pytest.mark.parametrize("missing", ["username", "userId", "password"])
def test_missing_field_rejected(client, missing):
    payload = {k: v for k, v in VALID_USER.items() if k != missing}
    res = client.post("/add_user", json=payload)

    assert res.status_code == 400
    assert res.get_json()["success"] is False


def test_no_json_body_rejected(client):
    res = client.post("/add_user")
    assert res.status_code == 400


def test_new_user_can_log_in(client):
    add_user(client)

    ok = client.post("/login", json={"userId": "jane123", "password": "secret"})
    assert ok.status_code == 200

    bad = client.post("/login", json={"userId": "jane123", "password": "wrong"})
    assert bad.status_code == 401