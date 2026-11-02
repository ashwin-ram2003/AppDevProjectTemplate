"""Tests for US-03 (create a project) and US-05 (view my projects).

H1 (seeded by conftest.py's `mongo` fixture, with members alice and bob)
exists before every test here; these tests cover projects created or
listed on top of it.
"""

import pytest

import projectsDatabase as projectsDB


def _create(api, projectId, projectName, description, userId):
    return api.post(
        "/create_project",
        json={
            "projectId": projectId,
            "projectName": projectName,
            "description": description,
            "userId": userId,
        },
    )


def _list(api, userId):
    return api.post("/get_user_projects_list", json={"userId": userId})


def _info(api, projectId, userId):
    return api.post("/get_project_info", json={"projectId": projectId, "userId": userId})


# ---------------------------------------------------------------------------
# US-03 -- create a project
# ---------------------------------------------------------------------------


def test_creating_a_project_succeeds_and_returns_it(api):
    response = _create(api, "P2", "Robotics Club", "Shared lab hardware", "alice")

    assert response.status_code == 201
    assert response.get_json()["project"] == {
        "projectId": "P2",
        "projectName": "Robotics Club",
        "description": "Shared lab hardware",
        "users": ["alice"],
    }


def test_the_creator_is_automatically_a_member(api):
    _create(api, "P2", "Robotics Club", "Shared lab hardware", "alice")

    response = _info(api, "P2", "alice")

    assert response.status_code == 200
    assert response.get_json()["project"]["projectId"] == "P2"


@pytest.mark.parametrize("missingField", ["projectName", "projectId", "description", "userId"])
def test_missing_field_is_400(api, missingField):
    body = {
        "projectName": "Robotics Club",
        "projectId": "P2",
        "description": "Shared lab hardware",
        "userId": "alice",
    }
    del body[missingField]

    response = api.post("/create_project", json=body)

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_input", "field": missingField}


def test_creating_a_project_with_a_taken_id_is_409_and_does_not_overwrite_it(api):
    _create(api, "P2", "Robotics Club", "Shared lab hardware", "alice")

    response = _create(api, "P2", "Someone Else's Project", "Different description", "bob")

    assert response.status_code == 409
    assert response.get_json() == {"error": "project_already_exists", "field": "projectId"}

    # The original project is untouched -- bob was never added, and the
    # original name/description survive.
    original = _info(api, "P2", "alice").get_json()["project"]
    assert original["projectName"] == "Robotics Club"
    assert original["users"] == ["alice"]


def test_creating_a_project_that_collides_with_the_pre_existing_seeded_project_is_409(api):
    response = _create(api, "H1", "Collision", "Should not overwrite H1", "alice")

    assert response.status_code == 409
    assert response.get_json() == {"error": "project_already_exists", "field": "projectId"}


def test_direct_db_level_create_project_rejects_a_non_string_field(mongo):
    with pytest.raises(projectsDB.InvalidProjectInput) as caught:
        projectsDB.createProject(mongo, "Robotics Club", {"$ne": "P2"}, "desc", "alice")
    assert str(caught.value) == "projectId"


def test_direct_db_level_create_project_rejects_an_empty_string_field(mongo):
    with pytest.raises(projectsDB.InvalidProjectInput) as caught:
        projectsDB.createProject(mongo, "", "P2", "desc", "alice")
    assert str(caught.value) == "projectName"


# ---------------------------------------------------------------------------
# US-05 -- view my projects
# ---------------------------------------------------------------------------


def test_a_user_sees_every_project_they_belong_to(api):
    _create(api, "P2", "Robotics Club", "Shared lab hardware", "alice")
    _create(api, "P3", "Drone Team", "Shared drone parts", "alice")

    response = _list(api, "alice")

    assert response.status_code == 200
    projectIds = [project["projectId"] for project in response.get_json()["projects"]]
    # alice is seeded into H1 (conftest.py) plus the two just created here.
    assert projectIds == ["H1", "P2", "P3"]


def test_a_user_does_not_see_projects_they_do_not_belong_to(api):
    _create(api, "P2", "Robotics Club", "Shared lab hardware", "alice")

    response = _list(api, "bob")

    projectIds = [project["projectId"] for project in response.get_json()["projects"]]
    assert "P2" not in projectIds
    assert projectIds == ["H1"]  # bob is still seeded into H1 by conftest.py


def test_a_brand_new_user_with_no_projects_sees_an_empty_list(api):
    response = _list(api, "nobody-yet")

    assert response.status_code == 200
    assert response.get_json()["projects"] == []


def test_missing_user_id_is_400(api):
    response = api.post("/get_user_projects_list", json={})

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_input", "field": "userId"}


def test_joining_a_project_makes_it_show_up_in_the_list(api):
    _create(api, "P2", "Robotics Club", "Shared lab hardware", "alice")

    api.post("/join_project", json={"projectId": "P2", "userId": "bob"})

    response = _list(api, "bob")
    projectIds = [project["projectId"] for project in response.get_json()["projects"]]
    assert "P2" in projectIds


# ---------------------------------------------------------------------------
# GET /get_project_info
# ---------------------------------------------------------------------------


def test_get_project_info_for_a_member_succeeds(api):
    response = _info(api, "H1", "alice")

    assert response.status_code == 200
    assert response.get_json()["project"]["projectId"] == "H1"


def test_get_project_info_for_a_non_member_is_403(api):
    response = _info(api, "H1", "mallory")

    assert response.status_code == 403
    assert response.get_json() == {"error": "not_a_project_member"}


def test_get_project_info_for_an_unknown_project_is_403_not_404(api):
    # assertProjectMember runs first (the trust boundary every hardware
    # route also uses), so an unknown projectId looks the same as "not a
    # member" to a caller who was never told the project exists at all.
    response = _info(api, "NO-SUCH-PROJECT", "alice")

    assert response.status_code == 403
    assert response.get_json() == {"error": "not_a_project_member"}


@pytest.mark.parametrize("missingField", ["projectId", "userId"])
def test_get_project_info_missing_field_is_400(api, missingField):
    body = {"projectId": "H1", "userId": "alice"}
    del body[missingField]

    response = api.post("/get_project_info", json=body)

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_input", "field": missingField}
