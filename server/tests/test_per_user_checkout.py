"""Tests for per-user checkout accountability.

Reproduces the exact bug report this feature fixes: alice checks out 5
units of a hardware set, then bob -- who never checked out anything --
could check those same 5 back in. Checkin must be gated by what the
calling user personally holds (hardwareDatabase.py's `checkedOutBy`), not
the project-wide `checkedOut` total.
"""

import pytest

import hardwareDatabase as hardwareDB
import projectsDatabase as projectsDB


def _checkout(api, projectId, userId, hwSetName, quantity):
    return api.post(
        "/api/hardware/checkout",
        json={"projectId": projectId, "userId": userId, "hwSetName": hwSetName, "quantity": quantity},
    )


def _checkin(api, projectId, userId, hwSetName, quantity):
    return api.post(
        "/api/hardware/checkin",
        json={"projectId": projectId, "userId": userId, "hwSetName": hwSetName, "quantity": quantity},
    )


def _fetch(api, projectId, userId):
    return api.get(f"/api/hardware?projectId={projectId}&userId={userId}")


@pytest.fixture
def bob_in_project(mongo):
    """H1 is seeded with members alice and bob (see conftest.py's `mongo`
    fixture) -- nothing extra needed here beyond naming the fixture for
    readability at each test's seed_set call site.
    """
    return mongo


# ---------------------------------------------------------------------------
# The exact reported bug: user2 checking in what user1 checked out
# ---------------------------------------------------------------------------


def test_a_user_cannot_check_in_units_a_different_user_checked_out(api, seed_set, bob_in_project):
    seed_set("H1", "HWSet1", 10)
    _checkout(api, "H1", "alice", "HWSet1", 5)

    response = _checkin(api, "H1", "bob", "HWSet1", 5)

    assert response.status_code == 409
    body = response.get_json()
    assert body["error"] == "checkin_exceeds_checked_out"
    assert body["checkedOut"] == 0  # bob's own holding, not alice's or the project total
    assert body["requested"] == 5


def test_a_user_cannot_check_in_even_one_unit_of_what_someone_else_checked_out(api, seed_set, bob_in_project):
    seed_set("H1", "HWSet1", 10)
    _checkout(api, "H1", "alice", "HWSet1", 5)

    response = _checkin(api, "H1", "bob", "HWSet1", 1)

    assert response.status_code == 409


def test_the_user_who_checked_it_out_can_check_it_back_in(api, seed_set):
    seed_set("H1", "HWSet1", 10)
    _checkout(api, "H1", "alice", "HWSet1", 5)

    response = _checkin(api, "H1", "alice", "HWSet1", 5)

    assert response.status_code == 200
    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["available"] == 10
    assert hwSet["myCheckedOut"] == 0


def test_a_user_cannot_check_in_more_than_their_own_share_even_if_the_aggregate_covers_it(
    api, seed_set, bob_in_project
):
    """alice holds 5, bob holds 3 -- aggregate checked-out is 8. bob
    personally holds only 3, so bob checking in 5 must fail even though
    8 >= 5 project-wide. This is the crux of the fix."""
    seed_set("H1", "HWSet1", 20)
    _checkout(api, "H1", "alice", "HWSet1", 5)
    _checkout(api, "H1", "bob", "HWSet1", 3)

    response = _checkin(api, "H1", "bob", "HWSet1", 5)

    assert response.status_code == 409
    assert response.get_json()["checkedOut"] == 3  # bob's real share


# ---------------------------------------------------------------------------
# Each user's holding is tracked independently
# ---------------------------------------------------------------------------


def test_two_users_checking_out_the_same_set_are_tracked_independently(api, seed_set, bob_in_project):
    seed_set("H1", "HWSet1", 20)
    _checkout(api, "H1", "alice", "HWSet1", 5)
    _checkout(api, "H1", "bob", "HWSet1", 3)

    aliceView = _fetch(api, "H1", "alice").get_json()["hardwareSets"][0]
    bobView = _fetch(api, "H1", "bob").get_json()["hardwareSets"][0]

    # Shared, project-wide figures agree for both viewers...
    assert aliceView["available"] == bobView["available"] == 12
    assert aliceView["capacity"] == bobView["capacity"] == 20
    # ...but each viewer's personal figure reflects only their own share.
    assert aliceView["myCheckedOut"] == 5
    assert bobView["myCheckedOut"] == 3


def test_checking_out_more_after_already_holding_some_adds_to_the_running_total(api, seed_set):
    seed_set("H1", "HWSet1", 20)
    _checkout(api, "H1", "alice", "HWSet1", 2)
    response = _checkout(api, "H1", "alice", "HWSet1", 3)

    assert response.get_json()["hardwareSet"]["myCheckedOut"] == 5


def test_partial_checkin_reduces_only_that_users_own_holding(api, seed_set, bob_in_project):
    seed_set("H1", "HWSet1", 20)
    _checkout(api, "H1", "alice", "HWSet1", 5)
    _checkout(api, "H1", "bob", "HWSet1", 3)

    response = _checkin(api, "H1", "alice", "HWSet1", 2)

    assert response.status_code == 200
    assert response.get_json()["hardwareSet"]["myCheckedOut"] == 3  # alice: 5 - 2

    bobView = _fetch(api, "H1", "bob").get_json()["hardwareSets"][0]
    assert bobView["myCheckedOut"] == 3  # untouched by alice's checkin


# ---------------------------------------------------------------------------
# A brand-new user viewing a set they've never touched
# ---------------------------------------------------------------------------


def test_a_user_who_never_checked_anything_out_sees_zero(api, seed_set, bob_in_project):
    seed_set("H1", "HWSet1", 10)
    _checkout(api, "H1", "alice", "HWSet1", 4)

    bobView = _fetch(api, "H1", "bob").get_json()["hardwareSets"][0]
    assert bobView["myCheckedOut"] == 0


# ---------------------------------------------------------------------------
# Direct hardwareDatabase-level coverage (not just through the route layer)
# ---------------------------------------------------------------------------


def test_checkin_exceeds_checked_out_error_carries_the_callers_own_holding(mongo, seed_set):
    seed_set("H1", "HWSet1", 10)
    hardwareDB.checkoutHardware(mongo, "H1", "HWSet1", 5, "alice")

    with pytest.raises(hardwareDB.CheckinExceedsCheckedOutError) as caught:
        hardwareDB.checkinHardware(mongo, "H1", "HWSet1", 1, "bob")

    assert caught.value.checkedOut == 0
    assert caught.value.requested == 1


def test_checkedOutBy_rejects_a_non_string_userId(mongo, seed_set):
    seed_set("H1", "HWSet1", 10)
    with pytest.raises(hardwareDB.InvalidInventoryInput) as caught:
        hardwareDB.checkoutHardware(mongo, "H1", "HWSet1", 1, {"$ne": "alice"})
    assert str(caught.value) == "userId"


def test_get_project_hardware_status_reports_the_askers_own_holding(mongo, seed_set, bob_in_project):
    seed_set("H1", "HWSet1", 10)
    hardwareDB.checkoutHardware(mongo, "H1", "HWSet1", 4, "alice")

    aliceStatus = projectsDB.getProjectHardwareStatus(mongo, "H1", "alice")
    bobStatus = projectsDB.getProjectHardwareStatus(mongo, "H1", "bob")

    assert aliceStatus[0]["myCheckedOut"] == 4
    assert bobStatus[0]["myCheckedOut"] == 0
