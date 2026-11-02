"""Regression tests for the NoSQL-operator-injection guard: unvalidated
projectId/userId/reservationId/userName types allow injection that bypasses
project isolation.

request.get_json() decodes arbitrary JSON, so a client can POST a dict
(e.g. {"$ne": "..."}) in place of a plain string identifier. Mongo then
interprets that value as a query operator instead of an equality match,
which can match documents belonging to OTHER projects. Each test here
seeds a second project (P2) that the requesting user ("alice") is not a
member of, then attempts the injection against each of the mutating
hardware routes and asserts the request is rejected with P2's data left
completely untouched.
"""

import hardwareDatabase as hardwareDB
import projectsDatabase as projectsDB


def _seedOtherProject(mongo):
    """P2 belongs to "carol" only. alice (seeded by the `mongo` fixture as
    a member of H1) has no relationship to P2 and must never be able to
    read or mutate its hardware sets.
    """
    db = mongo[hardwareDB.DB_NAME]
    db[hardwareDB.PROJECTS_COLLECTION].insert_one(
        {"householdId": "P2", "users": ["carol"]}
    )
    db[hardwareDB.HARDWARE_SETS_COLLECTION].insert_one(
        {
            "projectId": "P2",
            "hwSetKey": "secrethwset",
            "hwSetName": "SecretHWSet",
            "capacity": 10,
            "reservations": [],
            "reservedQuantity": 0,
        }
    )


def _rawHardwareSet(mongo, projectId, hwSetKey):
    db = mongo[hardwareDB.DB_NAME]
    return db[hardwareDB.HARDWARE_SETS_COLLECTION].find_one(
        {"projectId": projectId, "hwSetKey": hwSetKey}
    )


# --- Route-level: dict projectId across all four mutating routes ----------


def test_checkin_rejects_dict_projectId_and_writes_nothing(api, mongo):
    _seedOtherProject(mongo)

    response = api.post(
        "/api/hardware/checkin",
        json={
            "projectId": {"$ne": "nope"},
            "userId": "alice",
            "hwSetName": "SecretHWSet",
            "quantity": 1,
        },
    )
    assert response.status_code in (400, 403)

    raw = _rawHardwareSet(mongo, "P2", "secrethwset")
    assert raw["capacity"] == 10


def test_checkout_rejects_dict_projectId_and_writes_nothing(api, mongo):
    _seedOtherProject(mongo)

    response = api.post(
        "/api/hardware/checkout",
        json={
            "projectId": {"$ne": "nope"},
            "userId": "alice",
            "hwSetName": "SecretHWSet",
            "quantity": 10,
        },
    )
    assert response.status_code in (400, 403)

    raw = _rawHardwareSet(mongo, "P2", "secrethwset")
    assert raw["capacity"] == 10


def test_checkout_rejects_list_projectId_and_writes_nothing(api, mongo):
    _seedOtherProject(mongo)

    response = api.post(
        "/api/hardware/checkout",
        json={
            "projectId": ["P2"],
            "userId": "alice",
            "hwSetName": "SecretHWSet",
            "quantity": 10,
        },
    )
    assert response.status_code in (400, 403)

    raw = _rawHardwareSet(mongo, "P2", "secrethwset")
    assert raw["capacity"] == 10


def test_request_rejects_dict_projectId_and_writes_nothing(api, mongo):
    _seedOtherProject(mongo)

    response = api.post(
        "/api/hardware/request",
        json={
            "projectId": {"$ne": "nope"},
            "userId": "alice",
            "userName": "Alice",
            "hwSetName": "SecretHWSet",
            "quantity": 5,
        },
    )
    assert response.status_code in (400, 403)

    raw = _rawHardwareSet(mongo, "P2", "secrethwset")
    assert raw["reservedQuantity"] == 0
    assert raw["reservations"] == []


def test_release_rejects_dict_projectId_and_writes_nothing(api, mongo):
    _seedOtherProject(mongo)
    db = mongo[hardwareDB.DB_NAME]
    db[hardwareDB.HARDWARE_SETS_COLLECTION].update_one(
        {"projectId": "P2", "hwSetKey": "secrethwset"},
        {
            "$push": {
                "reservations": {
                    "reservationId": "carol-resv-1",
                    "userId": "carol",
                    "userName": "Carol",
                    "quantity": 2,
                    "createdAt": "2026-06-01T00:00:00+00:00",
                }
            },
            "$inc": {"reservedQuantity": 2},
        },
    )

    response = api.post(
        "/api/hardware/release",
        json={
            "projectId": {"$ne": "nope"},
            "userId": "alice",
            "reservationId": "carol-resv-1",
        },
    )
    assert response.status_code == 403

    raw = _rawHardwareSet(mongo, "P2", "secrethwset")
    assert raw["reservedQuantity"] == 2
    assert len(raw["reservations"]) == 1


# --- reservationId injection (removeReservation) ---------------------------


def test_remove_reservation_rejects_dict_reservationId_and_writes_nothing(mongo):
    _seedOtherProject(mongo)
    db = mongo[hardwareDB.DB_NAME]
    db[hardwareDB.HARDWARE_SETS_COLLECTION].update_one(
        {"projectId": "P2", "hwSetKey": "secrethwset"},
        {
            "$push": {
                "reservations": {
                    "reservationId": "carol-resv-1",
                    "userId": "carol",
                    "userName": "Carol",
                    "quantity": 2,
                    "createdAt": "2026-06-01T00:00:00+00:00",
                }
            },
            "$inc": {"reservedQuantity": 2},
        },
    )

    try:
        hardwareDB.removeReservation(mongo, "P2", {"$ne": "nope"}, "carol")
        raised = False
    except hardwareDB.ReservationNotFoundError:
        raised = True
    assert raised

    raw = _rawHardwareSet(mongo, "P2", "secrethwset")
    assert raw["reservedQuantity"] == 2
    assert len(raw["reservations"]) == 1


def test_remove_reservation_rejects_list_reservationId_and_writes_nothing(mongo):
    _seedOtherProject(mongo)
    db = mongo[hardwareDB.DB_NAME]
    db[hardwareDB.HARDWARE_SETS_COLLECTION].update_one(
        {"projectId": "P2", "hwSetKey": "secrethwset"},
        {
            "$push": {
                "reservations": {
                    "reservationId": "carol-resv-1",
                    "userId": "carol",
                    "userName": "Carol",
                    "quantity": 2,
                    "createdAt": "2026-06-01T00:00:00+00:00",
                }
            },
            "$inc": {"reservedQuantity": 2},
        },
    )

    try:
        hardwareDB.removeReservation(mongo, "P2", ["carol-resv-1"], "carol")
        raised = False
    except hardwareDB.ReservationNotFoundError:
        raised = True
    assert raised

    raw = _rawHardwareSet(mongo, "P2", "secrethwset")
    assert raw["reservedQuantity"] == 2
    assert len(raw["reservations"]) == 1


# --- assertProjectMember: shared choke point --------------------------------


def test_assert_project_member_rejects_dict_projectId(mongo):
    try:
        projectsDB.assertProjectMember(mongo, {"$ne": "nope"}, "alice")
        raised = False
    except projectsDB.NotAHouseholdMemberError:
        raised = True
    assert raised


def test_assert_project_member_rejects_dict_userId(mongo):
    try:
        projectsDB.assertProjectMember(mongo, "H1", {"$ne": "nope"})
        raised = False
    except projectsDB.NotAHouseholdMemberError:
        raised = True
    assert raised


# --- userName injection (addReservation) ------------------------------------


def test_request_rejects_dict_userName_and_writes_nothing(api, mongo, seed_set):
    seed_set("H1", "HWSet1", 5)

    response = api.post(
        "/api/hardware/request",
        json={
            "projectId": "H1",
            "userId": "alice",
            "userName": {"$ne": "nope"},
            "hwSetName": "HWSet1",
            "quantity": 1,
        },
    )
    assert response.status_code == 400

    raw = _rawHardwareSet(mongo, "H1", "hwset1")
    assert raw["reservedQuantity"] == 0
    assert raw["reservations"] == []
