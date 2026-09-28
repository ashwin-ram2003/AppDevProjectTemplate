"""
End-to-end tracer test: checkin-then-read through the Flask test client
against mongomock, covering the tracer path plus its boundaries.
"""


def _checkin(api, **overrides):
    body = {
        "projectId": "H1",
        "userId": "alice",
        "hwSetName": "HWSet1",
        "quantity": 4,
    }
    body.update(overrides)
    return api.post("/api/hardware/checkin", json=body)


def _get_hardware_status(api, projectId="H1", userId="alice"):
    return api.get(f"/api/hardware?projectId={projectId}&userId={userId}")


def test_checkin_then_read_shows_hardware_set(api):
    response = _checkin(api, hwSetName="HWSet1", quantity=4)
    assert response.status_code == 201

    getResponse = _get_hardware_status(api)
    assert getResponse.status_code == 200
    hardwareSets = getResponse.get_json()["hardwareSets"]
    assert len(hardwareSets) == 1
    assert hardwareSets[0]["hwSetName"] == "HWSet1"
    assert hardwareSets[0]["capacity"] == 4
    assert hardwareSets[0]["available"] == 4


def test_second_checkin_of_normalized_name_merges_into_one_set(api):
    _checkin(api, hwSetName="HWSet1", quantity=4)
    secondResponse = _checkin(api, hwSetName=" hwset1 ", quantity=3)
    assert secondResponse.status_code == 201

    getResponse = _get_hardware_status(api)
    hardwareSets = getResponse.get_json()["hardwareSets"]
    assert len(hardwareSets) == 1
    assert hardwareSets[0]["capacity"] == 7


def test_multiple_hardware_sets_all_appear(api):
    _checkin(api, hwSetName="HWSet1", quantity=4)
    _checkin(api, hwSetName="HWSet2", quantity=10)

    getResponse = _get_hardware_status(api)
    hardwareSets = getResponse.get_json()["hardwareSets"]
    names = sorted(hwSet["hwSetName"] for hwSet in hardwareSets)
    assert names == ["HWSet1", "HWSet2"]


def test_get_status_rejects_non_member(api):
    _checkin(api, hwSetName="HWSet1", quantity=4)

    response = _get_hardware_status(api, userId="mallory")
    assert response.status_code == 403


def test_get_status_missing_parameters_returns_400(api):
    response = api.get("/api/hardware?userId=alice")
    assert response.status_code == 400

    response = api.get("/api/hardware?projectId=H1")
    assert response.status_code == 400


def test_full_checkin_request_checkout_release_flow(api):
    _checkin(api, hwSetName="HWSet1", quantity=10)

    reservationId = api.post(
        "/api/hardware/request",
        json={"projectId": "H1", "userId": "alice", "userName": "Alice", "hwSetName": "HWSet1", "quantity": 3},
    ).get_json()["requestId"]

    checkoutResponse = api.post(
        "/api/hardware/checkout",
        json={"projectId": "H1", "userId": "alice", "hwSetName": "HWSet1", "quantity": 5},
    )
    assert checkoutResponse.status_code == 200
    assert checkoutResponse.get_json()["hardwareSet"]["capacity"] == 5

    releaseResponse = api.post(
        "/api/hardware/release",
        json={"projectId": "H1", "userId": "alice", "requestId": reservationId},
    )
    assert releaseResponse.status_code == 200
    hwSet = releaseResponse.get_json()["hardwareSet"]
    assert hwSet["requestedQuantity"] == 0
    assert hwSet["capacity"] == 5
    assert hwSet["available"] == 5
