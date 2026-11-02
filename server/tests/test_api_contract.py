"""Contract tests every hardware route must satisfy (TD-09).

Each /api/hardware route has the same front door: identify the caller
(projectId + userId), confirm they belong to the project, and only then
touch any data. These tests walk that front door for every route in one
place, so a route that skips a step fails here even if its own feature
tests pass. A new route gets the same coverage by adding one line to
ROUTES.
"""

import pytest

import app as flask_app_module
import hardwareDatabase as hardwareDB

# method, path, a valid request, and the error code that route uses for a
# missing identity field. GET /api/hardware says "missing_parameter" while
# the POST routes say "invalid_input"; pinning each one here means a change
# to either is a deliberate API change rather than an accident.
ROUTES = [
    ("GET", "/api/hardware", {"projectId": "H1", "userId": "alice"}, "missing_parameter"),
    (
        "POST",
        "/api/hardware/create",
        {"projectId": "H1", "userId": "alice", "hwSetName": "NewSet", "capacity": 10},
        "invalid_input",
    ),
    (
        "POST",
        "/api/hardware/checkin",
        {"projectId": "H1", "userId": "alice", "hwSetName": "HWSet1", "quantity": 1},
        "invalid_input",
    ),
    (
        "POST",
        "/api/hardware/checkout",
        {"projectId": "H1", "userId": "alice", "hwSetName": "HWSet1", "quantity": 1},
        "invalid_input",
    ),
    (
        "POST",
        "/api/hardware/request",
        {"projectId": "H1", "userId": "alice", "userName": "Alice", "hwSetName": "HWSet1", "quantity": 1},
        "invalid_input",
    ),
    (
        "POST",
        "/api/hardware/release",
        {"projectId": "H1", "userId": "alice", "requestId": "no-such-request"},
        "invalid_input",
    ),
]

ROUTE_IDS = [path for _method, path, _payload, _code in ROUTES]


def _call(client, method, path, payload):
    if method == "GET":
        return client.get(path, query_string=payload)
    return client.post(path, json=payload)


def snapshot(mongo):
    """Every stored hardware-set document, in a stable order. Comparing a
    snapshot from before a rejected call with one from after is how these
    tests prove "rejected means nothing was written".
    """
    collection = mongo[hardwareDB.DB_NAME][hardwareDB.HARDWARE_SETS_COLLECTION]
    return sorted(
        collection.find({}, {"_id": 0}),
        key=lambda doc: (doc.get("projectId"), doc.get("hwSetKey")),
    )


@pytest.fixture
def stocked(mongo, seed_set):
    """H1 with HWSet1 (capacity 10) and 3 units already checked out, so a
    rejected checkout, checkin or request has something real it could
    have wrongly changed.
    """
    seed_set("H1", "HWSet1", 10)
    hardwareDB.checkoutHardware(mongo, "H1", "HWSet1", 3, "alice")
    return mongo


@pytest.mark.parametrize("missingField", ["projectId", "userId"])
@pytest.mark.parametrize("method,path,payload,missingCode", ROUTES, ids=ROUTE_IDS)
def test_missing_identity_field_is_400_and_writes_nothing(
    api, stocked, method, path, payload, missingCode, missingField
):
    before = snapshot(stocked)
    body = {key: value for key, value in payload.items() if key != missingField}

    response = _call(api, method, path, body)

    assert response.status_code == 400
    assert response.get_json() == {"error": missingCode, "field": missingField}
    assert snapshot(stocked) == before


@pytest.mark.parametrize("blankField", ["projectId", "userId"])
@pytest.mark.parametrize("method,path,payload,missingCode", ROUTES, ids=ROUTE_IDS)
def test_empty_string_identity_field_counts_as_missing(
    api, stocked, method, path, payload, missingCode, blankField
):
    response = _call(api, method, path, dict(payload, **{blankField: ""}))

    assert response.status_code == 400
    assert response.get_json() == {"error": missingCode, "field": blankField}


@pytest.mark.parametrize("method,path,payload,missingCode", ROUTES, ids=ROUTE_IDS)
def test_non_member_is_403_and_writes_nothing(api, stocked, method, path, payload, missingCode):
    before = snapshot(stocked)

    response = _call(api, method, path, dict(payload, userId="mallory"))

    assert response.status_code == 403
    assert response.get_json() == {"error": "not_a_project_member"}
    assert snapshot(stocked) == before


@pytest.mark.parametrize("method,path,payload,missingCode", ROUTES, ids=ROUTE_IDS)
def test_unknown_project_is_403_and_writes_nothing(api, stocked, method, path, payload, missingCode):
    before = snapshot(stocked)

    response = _call(api, method, path, dict(payload, projectId="NO-SUCH-PROJECT"))

    assert response.status_code == 403
    assert response.get_json() == {"error": "not_a_project_member"}
    assert snapshot(stocked) == before


@pytest.mark.parametrize(
    "method,path,payload,missingCode",
    [route for route in ROUTES if route[0] == "POST"],
    ids=[route[1] for route in ROUTES if route[0] == "POST"],
)
def test_malformed_json_body_is_a_400_not_a_500(api, stocked, method, path, payload, missingCode):
    """A body that isn't JSON at all is treated as an empty body: the
    caller gets the same 400 as a missing projectId, never a crash.
    """
    response = api.post(path, data="{not json", content_type="application/json")

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_input", "field": "projectId"}


def test_connection_string_comes_only_from_the_environment(monkeypatch):
    """No connection string is hard-coded anywhere (TD-07): whatever is in
    MONGODB_URI is exactly what the driver gets.
    """
    seen = []
    monkeypatch.setattr(flask_app_module, "MongoClient", lambda uri: seen.append(uri) or "client")
    monkeypatch.setenv("MONGODB_URI", "mongodb://db.example.invalid:27017/")

    assert flask_app_module.getMongoClient() == "client"
    assert seen == ["mongodb://db.example.invalid:27017/"]


@pytest.mark.parametrize("method,path,payload,missingCode", ROUTES, ids=ROUTE_IDS)
def test_database_not_configured_is_a_json_503(monkeypatch, method, path, payload, missingCode):
    """With no MONGODB_URI (a fresh deploy before the secret is set), every
    data route must answer with actionable JSON instead of a stack trace.
    Uses the real getMongoClient, unlike every other test in the suite.
    """
    monkeypatch.delenv("MONGODB_URI", raising=False)
    flask_app_module.app.testing = True
    client = flask_app_module.app.test_client()

    response = _call(client, method, path, payload)

    assert response.status_code == 503
    body = response.get_json()
    assert body["error"] == "database_not_configured"
    assert "MONGODB_URI" in body["detail"]
