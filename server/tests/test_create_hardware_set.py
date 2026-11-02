"""Tests for creating a hardware set with a starting capacity.

Before this, there was no route (or UI) that could ever call
hardwareDatabase.createHardwareSet -- a hardware set could only be seeded
directly against the database (test fixtures, or a manual script), never
through the app. These tests cover POST /api/hardware/create end to end,
plus the projectsDatabase wrapper's membership check.
"""

import pytest

import hardwareDatabase as hardwareDB
import projectsDatabase as projectsDB


def _create(api, projectId, userId, hwSetName, capacity):
    return api.post(
        "/api/hardware/create",
        json={"projectId": projectId, "userId": userId, "hwSetName": hwSetName, "capacity": capacity},
    )


def test_a_project_member_can_create_a_hardware_set(api):
    response = _create(api, "H1", "alice", "NewSet", 10)

    assert response.status_code == 201
    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["hwSetName"] == "NewSet"
    assert hwSet["capacity"] == 10
    assert hwSet["available"] == 10
    assert hwSet["myCheckedOut"] == 0


def test_the_new_set_is_immediately_visible_in_the_project_status(api):
    _create(api, "H1", "alice", "NewSet", 10)

    response = api.get("/api/hardware?projectId=H1&userId=alice")

    names = [hwSet["hwSetName"] for hwSet in response.get_json()["hardwareSets"]]
    assert "NewSet" in names


def test_a_non_member_cannot_create_a_hardware_set(api, seed_set):
    seed_set("H1", "ExistingSet", 10)

    response = _create(api, "H1", "mallory", "NewSet", 10)

    assert response.status_code == 403
    assert response.get_json() == {"error": "not_a_project_member"}
    names = [hwSet["hwSetName"] for hwSet in api.get("/api/hardware?projectId=H1&userId=alice").get_json()["hardwareSets"]]
    assert "NewSet" not in names


@pytest.mark.parametrize(
    "field,value,expectedField",
    [
        ("capacity", None, "capacity"),
        ("capacity", 0, "capacity"),
        ("capacity", -5, "capacity"),
        ("capacity", "ten", "capacity"),
        ("hwSetName", "", "hwSetName"),
        ("hwSetName", "   ", "hwSetName"),
        ("hwSetName", None, "hwSetName"),
    ],
)
def test_invalid_hwSetName_or_capacity_is_400(api, field, value, expectedField):
    body = {"projectId": "H1", "userId": "alice", "hwSetName": "NewSet", "capacity": 10}
    body[field] = value

    response = api.post("/api/hardware/create", json=body)

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_input", "field": expectedField}


def test_creating_a_set_that_already_exists_is_idempotent_and_does_not_reset_its_stock(api, seed_set):
    seed_set("H1", "ExistingSet", 10)

    # Check something out first, then "create" the same set again with a
    # different capacity -- the original capacity and live stock must survive.
    api.post(
        "/api/hardware/checkout",
        json={"projectId": "H1", "userId": "alice", "hwSetName": "ExistingSet", "quantity": 4},
    )

    response = _create(api, "H1", "alice", "ExistingSet", 999)

    assert response.status_code == 201
    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["capacity"] == 10  # untouched, not overwritten to 999
    assert hwSet["available"] == 6  # the earlier checkout still holds


def test_names_are_case_and_whitespace_insensitive_with_the_same_existing_set(api, seed_set):
    seed_set("H1", "NewSet", 10)

    response = _create(api, "H1", "alice", "  newset  ", 10)

    assert response.status_code == 201
    # Same underlying set, not a second one -- the display name from
    # creation is preserved.
    names = [hwSet["hwSetName"] for hwSet in api.get("/api/hardware?projectId=H1&userId=alice").get_json()["hardwareSets"]]
    assert names.count("NewSet") == 1


def test_direct_db_level_wrapper_checks_membership_before_creating(mongo):
    with pytest.raises(projectsDB.NotAHouseholdMemberError):
        projectsDB.createHardwareSet(mongo, "H1", "mallory", "NewSet", 10)


def test_direct_db_level_wrapper_rejects_invalid_capacity(mongo):
    with pytest.raises(hardwareDB.InvalidInventoryInput) as caught:
        projectsDB.createHardwareSet(mongo, "H1", "alice", "NewSet", 0)
    assert str(caught.value) == "capacity"
