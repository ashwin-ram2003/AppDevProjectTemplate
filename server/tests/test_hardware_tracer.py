"""
End-to-end tracer test: seed -> read -> checkout -> checkin through the Flask
test client against mongomock, covering the tracer path plus its boundaries.
"""


def _post(api, path, **overrides):
    body = {"projectId": "H1", "userId": "alice", "hwSetName": "HWSet1", "quantity": 4}
    body.update(overrides)
    return api.post(path, json=body)


def _get_hardware_status(api, projectId="H1", userId="alice"):
    return api.get(f"/api/hardware?projectId={projectId}&userId={userId}")


def test_seeded_set_is_readable_with_full_availability(api, seed_set):
    seed_set("H1", "HWSet1", 4)

    getResponse = _get_hardware_status(api)
    assert getResponse.status_code == 200
    assert getResponse.get_json()["projectId"] == "H1"
    hardwareSets = getResponse.get_json()["hardwareSets"]
    assert len(hardwareSets) == 1
    assert hardwareSets[0]["hwSetName"] == "HWSet1"
    assert hardwareSets[0]["capacity"] == 4
    assert hardwareSets[0]["available"] == 4


def test_create_hardware_set_is_idempotent_and_keeps_capacity(api, seed_set):
    seed_set("H1", "HWSet1", 4)
    seed_set("H1", " hwset1 ", 99)

    hardwareSets = _get_hardware_status(api).get_json()["hardwareSets"]
    assert len(hardwareSets) == 1
    assert hardwareSets[0]["capacity"] == 4


def test_multiple_hardware_sets_all_appear(api, seed_set):
    seed_set("H1", "HWSet1", 4)
    seed_set("H1", "HWSet2", 10)

    hardwareSets = _get_hardware_status(api).get_json()["hardwareSets"]
    assert sorted(hwSet["hwSetName"] for hwSet in hardwareSets) == ["HWSet1", "HWSet2"]


def test_get_status_rejects_non_member(api, seed_set):
    seed_set("H1", "HWSet1", 4)

    assert _get_hardware_status(api, userId="mallory").status_code == 403


def test_get_status_missing_parameters_returns_400(api):
    response = api.get("/api/hardware?userId=alice")
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing_parameter", "field": "projectId"}

    response = api.get("/api/hardware?projectId=H1")
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing_parameter", "field": "userId"}


def test_full_request_checkout_checkin_release_flow(api, seed_set):
    seed_set("H1", "HWSet1", 10)

    reservationId = api.post(
        "/api/hardware/request",
        json={"projectId": "H1", "userId": "alice", "userName": "Alice", "hwSetName": "HWSet1", "quantity": 3},
    ).get_json()["requestId"]

    checkoutResponse = _post(api, "/api/hardware/checkout", quantity=5)
    assert checkoutResponse.status_code == 200
    hwSet = checkoutResponse.get_json()["hardwareSet"]
    assert hwSet["capacity"] == 10
    assert hwSet["available"] == 5

    checkinResponse = _post(api, "/api/hardware/checkin", quantity=2)
    assert checkinResponse.status_code == 200
    hwSet = checkinResponse.get_json()["hardwareSet"]
    assert hwSet["capacity"] == 10
    assert hwSet["available"] == 7

    releaseResponse = api.post(
        "/api/hardware/release",
        json={"projectId": "H1", "userId": "alice", "requestId": reservationId},
    )
    assert releaseResponse.status_code == 200
    hwSet = releaseResponse.get_json()["hardwareSet"]
    assert hwSet["requestedQuantity"] == 0
    assert hwSet["capacity"] == 10
    assert hwSet["available"] == 7
