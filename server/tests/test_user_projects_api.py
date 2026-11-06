"""Tests for listing a user's projects (issue #6: View My Projects)."""

from pymongo.errors import PyMongoError

from server.app import create_app
from server.dummyProjectData import InMemoryProjectCollection


PROJECTS = [
    {
        "projectName": "Robot Arm",
        "projectId": "robot-arm",
        "description": "Senior design prototype",
        "hwSets": {},
        "users": ["sydney", "alice"],
    },
    {
        "projectName": "alpha drone",
        "projectId": "alpha-drone",
        "description": "",
        "hwSets": {"HWSet1": 5},
        "users": ["sydney"],
    },
    {
        "projectName": "Alice Only",
        "projectId": "alice-only",
        "description": "",
        "hwSets": {},
        "users": ["alice"],
    },
]

USERS = [
    {"username": "sydney", "userId": "sydney", "projects": []},
    {"username": "alice", "userId": "alice", "projects": []},
    {"username": "newbie", "userId": "newbie", "projects": []},
]


def make_client(projects=None, users=None):
    """Build a test client; pass users=None to mimic dummy mode (no user DB)."""
    app = create_app(
        {"TESTING": True},
        hardware_collection=InMemoryProjectCollection([]),
        projects_collection=projects or InMemoryProjectCollection(PROJECTS),
        user_collection=users,
    )
    return app.test_client()


# --- Success cases --------------------------------------------------------

def test_lists_only_the_users_projects_sorted_by_name():
    response = make_client().get("/api/users/sydney/projects")

    assert response.status_code == 200
    ids = [project["projectId"] for project in response.get_json()["projects"]]
    # Sorted case-insensitively: "alpha drone" before "Robot Arm".
    assert ids == ["alpha-drone", "robot-arm"]


def test_returns_full_project_details():
    response = make_client().get("/api/users/sydney/projects")

    robot_arm = response.get_json()["projects"][1]
    assert robot_arm == {
        "projectName": "Robot Arm",
        "projectId": "robot-arm",
        "description": "Senior design prototype",
        "hwSets": {},
        "users": ["sydney", "alice"],
    }


def test_user_with_no_projects_gets_empty_list():
    client = make_client(users=InMemoryProjectCollection(USERS))

    response = client.get("/api/users/newbie/projects")

    assert response.status_code == 200
    assert response.get_json() == {"projects": []}


def test_created_and_joined_projects_both_show_up():
    client = make_client()
    client.post(
        "/api/projects",
        json={"projectName": "Mine", "projectId": "mine", "userId": "bob"},
    )
    client.post("/api/projects/alice-only/users", json={"userId": "bob"})

    response = client.get("/api/users/bob/projects")

    ids = [project["projectId"] for project in response.get_json()["projects"]]
    assert ids == ["alice-only", "mine"]


# --- Error cases ----------------------------------------------------------

def test_unknown_user_returns_404_when_user_db_exists():
    client = make_client(users=InMemoryProjectCollection(USERS))

    response = client.get("/api/users/ghost/projects")

    assert response.status_code == 404
    assert response.get_json() == {"error": "User 'ghost' was not found."}


def test_blank_user_id_returns_400():
    response = make_client().get("/api/users/%20/projects")

    assert response.status_code == 400
    assert response.get_json() == {"error": "User ID is required."}


def test_database_error_returns_503():
    class BrokenCollection(InMemoryProjectCollection):
        def find(self, query):
            raise PyMongoError("down")

    response = make_client(projects=BrokenCollection([])).get(
        "/api/users/sydney/projects"
    )

    assert response.status_code == 503
    assert response.get_json() == {"error": "Projects are temporarily unavailable."}
