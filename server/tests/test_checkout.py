"""Tests for POST /api/hardware/checkout and /api/hardware/checkin
(server/hardwareDatabase.checkoutHardware / checkinHardware).

`capacity` is fixed: checkout and checkin only move the checked-out count,
so availability changes while capacity never does. Checkout beyond what is
available and checkin beyond what is checked out are both rejected without
writing anything. Requests never gate checkout.
"""

import hardwareDatabase as hardwareDB


def _post(api, path, projectId, userId, hwSetName, quantity):
    return api.post(
        path,
        json={"projectId": projectId, "userId": userId, "hwSetName": hwSetName, "quantity": quantity},
    )


def _checkout(api, projectId, userId, hwSetName, quantity):
    return _post(api, "/api/hardware/checkout", projectId, userId, hwSetName, quantity)


def _checkin(api, projectId, userId, hwSetName, quantity):
    return _post(api, "/api/hardware/checkin", projectId, userId, hwSetName, quantity)


def _rawHardwareSet(mongo, projectId, hwSetKey):
    db = mongo[hardwareDB.DB_NAME]
    return db[hardwareDB.HARDWARE_SETS_COLLECTION].find_one(
        {"projectId": projectId, "hwSetKey": hwSetKey}
    )


def test_checkout_reduces_availability_but_not_capacity(api, seed_set):
    seed_set("H1", "HWSet1", 10)

    response = _checkout(api, "H1", "alice", "HWSet1", 4)
    assert response.status_code == 200
    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["capacity"] == 10
    assert hwSet["available"] == 6


def test_checkout_rejects_quantity_exceeding_available(api, mongo, seed_set):
    seed_set("H1", "HWSet1", 5)
    _checkout(api, "H1", "alice", "HWSet1", 3)

    response = _checkout(api, "H1", "alice", "HWSet1", 4)
    assert response.status_code == 409
    body = response.get_json()
    assert body["error"] == "insufficient_stock"
    assert body["onHand"] == 2
    assert body["requested"] == 4

    raw = _rawHardwareSet(mongo, "H1", "hwset1")
    assert raw["capacity"] == 5
    assert raw["checkedOut"] == 3


def test_checkin_raises_availability_but_not_capacity(api, seed_set):
    seed_set("H1", "HWSet1", 10)
    _checkout(api, "H1", "alice", "HWSet1", 6)

    response = _checkin(api, "H1", "alice", "HWSet1", 2)
    assert response.status_code == 200
    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["capacity"] == 10
    assert hwSet["available"] == 6


def test_checkin_rejects_quantity_exceeding_checked_out(api, mongo, seed_set):
    seed_set("H1", "HWSet1", 10)
    _checkout(api, "H1", "alice", "HWSet1", 2)

    response = _checkin(api, "H1", "alice", "HWSet1", 3)
    assert response.status_code == 409
    body = response.get_json()
    assert body["error"] == "checkin_exceeds_checked_out"
    assert body["checkedOut"] == 2
    assert body["requested"] == 3

    raw = _rawHardwareSet(mongo, "H1", "hwset1")
    assert raw["capacity"] == 10
    assert raw["checkedOut"] == 2


def test_checkout_ignores_outstanding_requests(api, seed_set):
    """A request is a coordination signal, never a hold."""
    seed_set("H1", "HWSet1", 10)
    api.post(
        "/api/hardware/request",
        json={"projectId": "H1", "userId": "alice", "userName": "Alice", "hwSetName": "HWSet1", "quantity": 8},
    )

    response = _checkout(api, "H1", "alice", "HWSet1", 10)
    assert response.status_code == 200
    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["capacity"] == 10
    assert hwSet["available"] == 0


def test_checkout_and_checkin_unknown_hardware_set_return_404(api):
    assert _checkout(api, "H1", "alice", "NoSuchSet", 1).status_code == 404
    assert _checkin(api, "H1", "alice", "NoSuchSet", 1).status_code == 404


def test_checkout_and_checkin_reject_non_positive_quantity(api, seed_set):
    seed_set("H1", "HWSet1", 10)

    for call in (_checkout, _checkin):
        response = call(api, "H1", "alice", "HWSet1", 0)
        assert response.status_code == 400
        assert response.get_json()["field"] == "quantity"


def test_checkin_rejects_non_member(api):
    assert _checkin(api, "H1", "mallory", "HWSet1", 1).status_code == 403
