"""Tests for POST /api/hardware/checkout (server/hardwareDatabase.checkoutHardware).

Covers the overbooking guard reading `capacity` rather than `availability`
(checkout draws from total stock regardless of outstanding requests), that a
rejected checkout leaves capacity untouched, and that requests never gate
checkout.
"""

import hardwareDatabase as hardwareDB


def _checkin(api, projectId, userId, hwSetName, quantity):
    response = api.post(
        "/api/hardware/checkin",
        json={
            "projectId": projectId,
            "userId": userId,
            "hwSetName": hwSetName,
            "quantity": quantity,
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["hardwareSet"]


def _checkout(api, projectId, userId, hwSetName, quantity):
    return api.post(
        "/api/hardware/checkout",
        json={
            "projectId": projectId,
            "userId": userId,
            "hwSetName": hwSetName,
            "quantity": quantity,
        },
    )


def _rawHardwareSet(mongo, projectId, hwSetKey):
    db = mongo[hardwareDB.DB_NAME]
    return db[hardwareDB.HARDWARE_SETS_COLLECTION].find_one(
        {"projectId": projectId, "hwSetKey": hwSetKey}
    )


def test_checkin_creates_hardware_set_with_full_availability(api):
    hwSet = _checkin(api, "H1", "alice", "HWSet1", 10)
    assert hwSet["capacity"] == 10
    assert hwSet["available"] == 10
    assert hwSet["hwSetName"] == "HWSet1"


def test_checkin_merges_into_existing_set_by_normalized_name(api):
    _checkin(api, "H1", "alice", "HWSet1", 5)
    hwSet = _checkin(api, "H1", "alice", " hwset1 ", 3)
    assert hwSet["capacity"] == 8
    assert hwSet["hwSetName"] == "HWSet1"  # first-seen display name is kept


def test_checkout_reduces_capacity(api):
    _checkin(api, "H1", "alice", "HWSet1", 10)

    response = _checkout(api, "H1", "alice", "HWSet1", 4)
    assert response.status_code == 200
    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["capacity"] == 6
    assert hwSet["available"] == 6


def test_checkout_rejects_quantity_exceeding_capacity(api, mongo):
    _checkin(api, "H1", "alice", "HWSet1", 5)

    response = _checkout(api, "H1", "alice", "HWSet1", 10)
    assert response.status_code == 409
    body = response.get_json()
    assert body["error"] == "insufficient_stock"
    assert body["onHand"] == 5
    assert body["requested"] == 10

    raw = _rawHardwareSet(mongo, "H1", "hwset1")
    assert raw["capacity"] == 5


def test_checkout_ignores_outstanding_requests_when_checking_capacity(api):
    """Checkout draws from total capacity, not (capacity - reservedQuantity)
    -- a request is a coordination signal, never a hold.
    """
    _checkin(api, "H1", "alice", "HWSet1", 10)
    api.post(
        "/api/hardware/request",
        json={
            "projectId": "H1",
            "userId": "alice",
            "userName": "Alice",
            "hwSetName": "HWSet1",
            "quantity": 8,
        },
    )

    response = _checkout(api, "H1", "alice", "HWSet1", 10)
    assert response.status_code == 200
    hwSet = response.get_json()["hardwareSet"]
    assert hwSet["capacity"] == 0


def test_checkout_unknown_hardware_set_returns_404(api):
    response = _checkout(api, "H1", "alice", "NoSuchSet", 1)
    assert response.status_code == 404


def test_checkout_rejects_non_positive_quantity(api):
    _checkin(api, "H1", "alice", "HWSet1", 10)

    response = _checkout(api, "H1", "alice", "HWSet1", 0)
    assert response.status_code == 400
    assert response.get_json()["field"] == "quantity"


def test_checkin_rejects_non_member(api):
    response = api.post(
        "/api/hardware/checkin",
        json={
            "projectId": "H1",
            "userId": "mallory",
            "hwSetName": "HWSet1",
            "quantity": 1,
        },
    )
    assert response.status_code == 403
