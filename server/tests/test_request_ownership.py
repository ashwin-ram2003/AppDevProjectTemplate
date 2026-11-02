"""Who may release a request (US-08a, TD-09).

Only the member who made a request can take it back. The two ways to be
refused are deliberately different: a stranger to the project gets
not_a_project_member, while a teammate releasing someone else's request
gets not_your_reservation. Both are 403, so these tests pin the error
code, not just the status.
"""

import pytest

import hardwareDatabase as hardwareDB


def _collection(mongo):
    return mongo[hardwareDB.DB_NAME][hardwareDB.HARDWARE_SETS_COLLECTION]


def snapshot(mongo):
    return sorted(_collection(mongo).find({}, {"_id": 0}), key=lambda doc: doc.get("hwSetKey"))


def rawHardwareSet(mongo, projectId, hwSetKey):
    return _collection(mongo).find_one({"projectId": projectId, "hwSetKey": hwSetKey})


def requestUnits(api, quantity, userId="alice", userName="Alice"):
    return api.post(
        "/api/hardware/request",
        json={
            "projectId": "H1",
            "userId": userId,
            "userName": userName,
            "hwSetName": "HWSet1",
            "quantity": quantity,
        },
    )


def release(api, requestId, userId="alice"):
    return api.post(
        "/api/hardware/release",
        json={"projectId": "H1", "userId": userId, "requestId": requestId},
    )


@pytest.fixture(autouse=True)
def hwSet1(seed_set):
    """Every test here starts with HWSet1 (capacity 10) in project H1."""
    return seed_set("H1", "HWSet1", 10)


def _requestAs(api, userId, userName, quantity):
    response = requestUnits(api, quantity, userId=userId, userName=userName)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["requestId"]


def test_owner_can_release_their_request(api, mongo):
    requestId = _requestAs(api, "alice", "Alice", 3)

    response = release(api, requestId, userId="alice")

    assert response.status_code == 200
    assert response.get_json()["hardwareSet"]["requests"] == []
    assert rawHardwareSet(mongo, "H1", "hwset1")["reservedQuantity"] == 0


def test_teammate_cannot_release_someone_elses_request(api, mongo):
    requestId = _requestAs(api, "alice", "Alice", 3)
    before = snapshot(mongo)

    response = release(api, requestId, userId="bob")

    assert response.status_code == 403
    assert response.get_json() == {"error": "not_your_reservation"}
    assert snapshot(mongo) == before


def test_non_member_is_refused_before_ownership_is_considered(api, mongo):
    requestId = _requestAs(api, "alice", "Alice", 3)
    before = snapshot(mongo)

    response = release(api, requestId, userId="mallory")

    assert response.status_code == 403
    assert response.get_json() == {"error": "not_a_project_member"}
    assert snapshot(mongo) == before


def test_releasing_twice_is_404_the_second_time_and_never_goes_negative(api, mongo):
    requestId = _requestAs(api, "alice", "Alice", 3)

    assert release(api, requestId).status_code == 200
    second = release(api, requestId)

    assert second.status_code == 404
    assert second.get_json() == {"error": "reservation_not_found"}
    assert rawHardwareSet(mongo, "H1", "hwset1")["reservedQuantity"] == 0


def test_releasing_one_request_leaves_the_others_alone(api, mongo):
    _requestAs(api, "alice", "Alice", 2)
    middle = _requestAs(api, "alice", "Alice", 3)
    _requestAs(api, "bob", "Bob", 4)

    response = release(api, middle)

    hwSet = response.get_json()["hardwareSet"]
    assert [(entry["userId"], entry["quantity"]) for entry in hwSet["requests"]] == [("alice", 2), ("bob", 4)]
    assert hwSet["requestedQuantity"] == 6
    # Requests are a heads-up, not a hold: availability ignores them.
    assert hwSet["available"] == 10


def test_release_without_a_request_id_is_404(api):

    response = api.post("/api/hardware/release", json={"projectId": "H1", "userId": "alice"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "reservation_not_found"}


def test_releasing_a_request_never_changes_capacity(api, mongo):
    requestId = _requestAs(api, "alice", "Alice", 3)

    release(api, requestId)

    assert rawHardwareSet(mongo, "H1", "hwset1")["capacity"] == 10
