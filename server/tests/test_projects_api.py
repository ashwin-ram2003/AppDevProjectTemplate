from copy import deepcopy

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from server.app import create_app
from server.dummyProjectData import InMemoryProjectCollection


EXISTING = [
    {
        "projectName": "Existing Project",
        "projectId": "existing",
        "description": "Already here",
        "hwSets": {},
        "users": ["alice"],
    },
]


def make_client(projects_collection=None):
    app = create_app(
        {"TESTING": True},
        hardware_collection=InMemoryProjectCollection([]),
        projects_collection=projects_collection
        or InMemoryProjectCollection(EXISTING),
    )
    return app.test_client()


def valid_body(**overrides):
    body = {
        "projectName": "Robot Arm",
        "projectId": "robot-arm",
        "description": "Senior design prototype",
        "userId": "sydney",
    }
    body.update(overrides)
    return body


def test_create_project_returns_201_and_project():
    response = make_client().post("/api/projects", json=valid_body())

    assert response.status_code == 201
    assert response.get_json() == {
        "projectName": "Robot Arm",
        "projectId": "robot-arm",
        "description": "Senior design prototype",
        "hwSets": {},
        "users": ["sydney"],
    }


def test_created_project_can_be_fetched():
    client = make_client()
    client.post("/api/projects", json=valid_body())

    response = client.get("/api/projects/robot-arm")

    assert response.status_code == 200
    assert response.get_json()["projectName"] == "Robot Arm"


def test_create_project_trims_whitespace_and_allows_missing_description():
    body = valid_body(projectName="  Robot Arm  ", projectId=" robot-arm ")
    del body["description"]

    response = make_client().post("/api/projects", json=body)

    assert response.status_code == 201
    assert response.get_json()["projectName"] == "Robot Arm"
    assert response.get_json()["projectId"] == "robot-arm"
    assert response.get_json()["description"] == ""


def test_create_project_without_user_returns_400():
    body = valid_body()
    del body["userId"]

    response = make_client().post("/api/projects", json=body)

    assert response.status_code == 400
    assert response.get_json()["error"] == "User ID is required."


def test_duplicate_project_id_returns_409():
    response = make_client().post(
        "/api/projects", json=valid_body(projectId="existing")
    )

    assert response.status_code == 409
    assert "already taken" in response.get_json()["error"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"projectName": ""},
        {"projectName": "   "},
        {"projectName": None},
        {"projectName": "x" * 101},
        {"projectId": ""},
        {"projectId": "has spaces"},
        {"projectId": "bad/slash"},
        {"projectId": "x" * 33},
        {"projectId": 123},
        {"description": 42},
        {"description": "x" * 1001},
    ],
)
def test_invalid_fields_return_400(overrides):
    response = make_client().post("/api/projects", json=valid_body(**overrides))

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_non_json_body_returns_400():
    response = make_client().post(
        "/api/projects", data="not json", content_type="text/plain"
    )

    assert response.status_code == 400


def test_unknown_project_returns_404():
    response = make_client().get("/api/projects/nope")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Project not found."}


class RacingCollection(InMemoryProjectCollection):
    """Simulates another request inserting the same ID between check and insert."""

    def insert_one(self, document):
        raise DuplicateKeyError("duplicate key")


def test_database_duplicate_key_race_returns_409():
    response = make_client(RacingCollection([])).post(
        "/api/projects", json=valid_body()
    )

    assert response.status_code == 409


class BrokenCollection(InMemoryProjectCollection):
    def find_one(self, query):
        raise PyMongoError("database down")


def test_database_error_returns_503():
    client = make_client(BrokenCollection([]))

    assert client.post("/api/projects", json=valid_body()).status_code == 503
    assert client.get("/api/projects/robot-arm").status_code == 503