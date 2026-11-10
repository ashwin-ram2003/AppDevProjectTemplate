import os
import sys

# Set mock object mongodb
os.environ["USE_MOCK_DB"] = "1"
os.environ["SKIP_SEED"] = "1"

# Import files from server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

import app as server


@pytest.fixture
def api():
    for db_name in ("HardwareCheckout", "Users", "Projects"):
        server.client.drop_database(db_name)
    server.seed_hardware_sets()
    server.app.config["TESTING"] = True

    return server.app.test_client()

# Create User
def make_user(c, userId, password="pw123", username=None):
    c.post("/add_user", json={"username": username or userId, "userId": userId, "password": password})

# Login to user
def login(c, userId, password="pw123"):
    return c.post("/login", json={"userId": userId, "password": password})


@pytest.fixture
def logged_in(api):
    make_user(api, "alice1", username="Alice")
    login(api, "alice1")
    return api

# Try two users accessing site
@pytest.fixture
def second_client():
    return server.app.test_client()