"""Tests for POST /api/hardware/request and /api/hardware/release
(server/hardwareDatabase.addReservation / removeReservation).

A "request" (SN3) is a non-binding coordination signal -- it never gates
checkout and is never compared against capacity. Only the member who
created a request can release it.
"""

import hardwareDatabase as hardwareDB


def _checkin(api, projectId, userId, hwSetName, quantity):
    response = api.post(
        "/api/hardware/checkin",
        json={"projectId": projectId, "userId": userId, "hwSetName": hwSetName, "quantity": quantity},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["hardwareSet"]


def _request(api, projectId, userId, userName, hwSetName, quantity):
    return api.post(
        "/api/hardware/request",
        json={
            "projectId": projectId,
            "userId": userId,
            "userName": userName,
            "hwSetName": hwSetName,
            "quantity": quantity,
        },
    )


def _release(api, projectId, userId, reservationId):
    return api.post(
        "/api/hardware/release",
        json={"projectId": projectId, "userId": userId, "requestId": reservationId},
    )


def test_request_adds_reservation_without_reducing_capacity(api):
    _checkin(api, "H1", "alice", "HWSet1", 10)

    response = _request(api, "H1", "alice", "Alice", "HWSet1", 4)
    assert response.status_code == 201
    body = response.get_json()
    hwSet = body["hardwareSet"]
    assert hwSet["capacity"] == 10
    assert hwSet["requestedQuantity"] == 4
    assert hwSet["available"] == 6
    assert len(hwSet["requests"]) == 1
    assert hwSet["requests"][0]["userId"] == "alice"
    assert hwSet["requests"][0]["quantity"] == 4


def test_request_never_compares_quantity_against_capacity(api):
    """Requesting more than is on hand is legitimate -- only checkout is
    guarded against overbooking.
    """
    _checkin(api, "H1", "alice", "HWSet1", 2)

    response = _request(api, "H1", "alice", "Alice", "HWSet1", 100)
    assert response.status_code == 201
    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["requestedQuantity"] == 100


def test_request_unknown_hardware_set_returns_404(api):
    response = _request(api, "H1", "alice", "Alice", "NoSuchSet", 1)
    assert response.status_code == 404


def test_release_removes_reservation_and_restores_availability(api):
    _checkin(api, "H1", "alice", "HWSet1", 10)
    reservationId = _request(api, "H1", "alice", "Alice", "HWSet1", 3).get_json()["requestId"]

    response = _release(api, "H1", "alice", reservationId)
    assert response.status_code == 200
    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["requestedQuantity"] == 0
    assert hwSet["available"] == 10
    assert hwSet["requests"] == []


def test_release_by_non_owner_is_rejected(api):
    _checkin(api, "H1", "alice", "HWSet1", 10)
    reservationId = _request(api, "H1", "alice", "Alice", "HWSet1", 3).get_json()["requestId"]

    # bob is not a member of H1 -- membership check fires first.
    response = _release(api, "H1", "bob", reservationId)
    assert response.status_code == 403


def test_release_unknown_reservation_returns_404(api):
    response = _release(api, "H1", "alice", "not-a-real-id")
    assert response.status_code == 404


def test_two_simultaneous_requests_both_survive(api):
    _checkin(api, "H1", "alice", "HWSet1", 10)
    _request(api, "H1", "alice", "Alice", "HWSet1", 2)
    response = _request(api, "H1", "alice", "Alice", "HWSet1", 3)

    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["requestedQuantity"] == 5
    assert len(hwSet["requests"]) == 2
