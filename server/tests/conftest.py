import os
import sys

import mongomock
import pytest

# Insert the server directory onto sys.path so the DB modules import by
# their bare names (hardwareDatabase, projectsDatabase, app).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as flask_app_module  # noqa: E402
import hardwareDatabase as hardwareDB  # noqa: E402


@pytest.fixture
def mongo():
    """A mongomock.MongoClient seeded with one project document."""
    client = mongomock.MongoClient()
    db = client[hardwareDB.DB_NAME]
    db[hardwareDB.PROJECTS_COLLECTION].insert_one(
        {"householdId": "H1", "users": ["alice", "bob"]}
    )
    return client


@pytest.fixture
def api(mongo, monkeypatch):
    """A Flask test client with app.getMongoClient monkeypatched to return
    the seeded mongomock client.
    """
    monkeypatch.setattr(flask_app_module, "getMongoClient", lambda: mongo)
    flask_app_module.app.testing = True
    return flask_app_module.app.test_client()


@pytest.fixture
def seed_set(mongo):
    """seed_set(projectId, hwSetName, capacity) -> serialized hardware set."""
    def _seed(projectId, hwSetName, capacity):
        return hardwareDB.createHardwareSet(mongo, projectId, hwSetName, capacity)
    return _seed
