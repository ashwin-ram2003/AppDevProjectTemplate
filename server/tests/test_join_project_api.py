"""Tests for adding a user to a project (issue #5: Join a Project)."""

from pymongo.errors import PyMongoError

from server.app import create_app
from server.dummyProjectData import InMemoryProjectCollection


PROJECTS = [
    {
        "projectName": "Existing Project",
        "projectId": "existing",
        "description": "Already here",
        "hwSets": {},
        "users": ["alice"],
    },
]

USERS = [
    {"username": "alice", "userId": "alice", "projects": ["existing"]},
    {"username": "sydney", "userId": "sydney", "projects": []},
]


def make_app(projects=None, users=None):
    """Build an app; pass users=None to mimic dummy mode (no user DB)."""
    return create_app(
        {"TESTING": True},
        hardware_collection=InMemoryProjectCollection([]),
        projects_collection=projects or InMemoryProjectCollection(PROJECTS),
        user_collection=users,
    )


def join(client, project_id="existing", **body):
    body.setdefault("userId", "sydney")
    return client.post(f"/api/projects/{project_id}/users", json=body)


# --- Success cases --------------------------------------------------------

def test_join_adds_user_and_returns_project():
    response = join(make_app().test_client())

    assert response.status_code == 200
    assert response.get_json()["users"] == ["alice", "sydney"]


def test_joined_user_shows_up_when_project_is_fetched():
    client = make_app().test_client()
    join(client)

    project = client.get("/api/projects/existing").get_json()

    assert "sydney" in project["users"]


def test_join_trims_user_id_whitespace():
    response = join(make_app().test_client(), userId="  sydney  ")

    assert response.status_code == 200
    assert response.get_json()["users"] == ["alice", "sydney"]


# --- Error cases ----------------------------------------------------------

def test_joining_twice_returns_409_and_does_not_duplicate():
    client = make_app().test_client()
    join(client)

    response = join(client)

    assert response.status_code == 409
    assert "already a member" in response.get_json()["error"]
    assert client.get("/api/projects/existing").get_json()["users"] == [
        "alice",
        "sydney",
    ]


def test_unknown_project_returns_404():
    response = join(make_app().test_client(), project_id="nope")

    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


def test_missing_user_id_returns_400():
    client = make_app().test_client()

    for bad in ("", "   ", None, 42):
        response = join(client, userId=bad)
        assert response.status_code == 400, bad


def test_non_json_body_returns_400():
    response = make_app().test_client().post(
        "/api/projects/existing/users", data="nope", content_type="text/plain"
    )

    assert response.status_code == 400


# --- With a user database (like MongoDB mode) ------------------------------

def test_with_user_db_unknown_user_returns_404():
    users = InMemoryProjectCollection(USERS)
    response = join(make_app(users=users).test_client(), userId="ghost")

    assert response.status_code == 404
    assert "ghost" in response.get_json()["error"]


def test_with_user_db_project_is_added_to_users_projects():
    users = InMemoryProjectCollection(USERS)

    response = join(make_app(users=users).test_client())

    assert response.status_code == 200
    assert users.find_one({"userId": "sydney"})["projects"] == ["existing"]


# --- Edge cases -----------------------------------------------------------

class RacingCollection(InMemoryProjectCollection):
    """Another request adds the same user between our check and update."""

    def update_one(self, query, update):
        super().update_one({"projectId": query["projectId"]}, update)
        return super().update_one(query, update)


def test_concurrent_join_returns_409_without_duplicate():
    projects = RacingCollection(PROJECTS)

    response = join(make_app(projects=projects).test_client())

    assert response.status_code == 409
    assert projects.find_one({"projectId": "existing"})["users"] == [
        "alice",
        "sydney",
    ]


class BrokenCollection(InMemoryProjectCollection):
    def update_one(self, query, update):
        raise PyMongoError("database down")


def test_database_error_returns_503():
    response = join(make_app(projects=BrokenCollection(PROJECTS)).test_client())

    assert response.status_code == 503