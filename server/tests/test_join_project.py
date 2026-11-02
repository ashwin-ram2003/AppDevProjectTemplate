"""Tests for US-04 (Join a project): projectsDatabase.addUser,
usersDatabase.joinProject, and POST /join_project.

Context: a brand-new sign-up has no project membership, so the hardware
view 403s with not_a_project_member until something adds that userId to
a project's `users` list. This is that something.
"""

import pytest

import projectsDatabase as projectsDB
import usersDatabase as usersDB


# ---------------------------------------------------------------------------
# projectsDatabase.addUser
# ---------------------------------------------------------------------------


def test_add_user_adds_userId_to_the_project(mongo):
    projectsDB.addUser(mongo, "H1", "carol")

    project = mongo[projectsDB.hardwareDB.DB_NAME][
        projectsDB.hardwareDB.PROJECTS_COLLECTION
    ].find_one({"householdId": "H1"})
    assert "carol" in project["users"]


def test_add_user_does_not_remove_existing_members(mongo):
    projectsDB.addUser(mongo, "H1", "carol")

    project = mongo[projectsDB.hardwareDB.DB_NAME][
        projectsDB.hardwareDB.PROJECTS_COLLECTION
    ].find_one({"householdId": "H1"})
    assert set(project["users"]) == {"alice", "bob", "carol"}


def test_add_user_is_idempotent(mongo):
    projectsDB.addUser(mongo, "H1", "alice")  # already a member

    project = mongo[projectsDB.hardwareDB.DB_NAME][
        projectsDB.hardwareDB.PROJECTS_COLLECTION
    ].find_one({"householdId": "H1"})
    # $addToSet must not create a duplicate entry.
    assert project["users"].count("alice") == 1


def test_add_user_raises_for_unknown_project(mongo):
    with pytest.raises(projectsDB.ProjectNotFoundError):
        projectsDB.addUser(mongo, "NoSuchProject", "carol")


def test_add_user_rejects_non_string_projectId(mongo):
    # Defends the same injection path as assertProjectMember -- a dict
    # value here could otherwise be interpreted by Mongo as a query
    # operator instead of a literal match.
    with pytest.raises(projectsDB.ProjectNotFoundError):
        projectsDB.addUser(mongo, {"$ne": "H1"}, "carol")


# ---------------------------------------------------------------------------
# usersDatabase.joinProject
# ---------------------------------------------------------------------------


def test_users_join_project_delegates_to_projects_db(mongo):
    usersDB.joinProject(mongo, "carol", "H1")

    project = mongo[projectsDB.hardwareDB.DB_NAME][
        projectsDB.hardwareDB.PROJECTS_COLLECTION
    ].find_one({"householdId": "H1"})
    assert "carol" in project["users"]


def test_users_join_project_raises_for_unknown_project(mongo):
    with pytest.raises(projectsDB.ProjectNotFoundError):
        usersDB.joinProject(mongo, "carol", "NoSuchProject")


# ---------------------------------------------------------------------------
# POST /join_project
# ---------------------------------------------------------------------------


def _join_project(api, userId, projectId):
    return api.post("/join_project", json={"userId": userId, "projectId": projectId})


def test_join_project_route_adds_membership_and_unblocks_hardware_view(api, mongo):
    response = _join_project(api, "carol", "H1")
    assert response.status_code == 200
    assert response.get_json() == {"userId": "carol", "projectId": "H1"}

    # The whole point: carol can now load the hardware view she couldn't
    # load before joining.
    hardware = api.get("/api/hardware?projectId=H1&userId=carol")
    assert hardware.status_code == 200


def test_join_project_route_404s_for_unknown_project(api):
    response = _join_project(api, "carol", "NoSuchProject")
    assert response.status_code == 404


def test_join_project_route_requires_userId(api):
    response = api.post("/join_project", json={"projectId": "H1"})
    assert response.status_code == 400
    assert response.get_json()["field"] == "userId"


def test_join_project_route_requires_projectId(api):
    response = api.post("/join_project", json={"userId": "carol"})
    assert response.status_code == 400
    assert response.get_json()["field"] == "projectId"
