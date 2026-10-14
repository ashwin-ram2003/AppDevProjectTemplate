# Tests for app.py
# Run from the server/ folder with:  pytest -v
#
# These tests never touch the real Atlas cluster. MongoClient is swapped for
# mongomock (an in-memory fake MongoDB), so every test starts with an empty database.
#
# Two kinds of tests:
#   - Hardware routes run against the real hardwareDatabase.py
#   - User/project routes swap usersDB/projectsDB for fakes, so they test app.py's
#     own logic (validation, status codes, userId hashing) while teammates finish
#     usersDatabase.py and projectsDatabase.py

import mongomock
import pytest

import app as app_module
from encryption import protect_user_id


# ---------- Fixtures ----------

@pytest.fixture
def db_client(monkeypatch):
    # One shared in-memory database for the whole test
    fake = mongomock.MongoClient()
    # Every MongoClient(...) call in app.py gets this same fake client
    monkeypatch.setattr(app_module, "MongoClient", lambda *args, **kwargs: fake)
    return fake


@pytest.fixture
def client(db_client):
    # Flask test client: lets us send requests without starting a server
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


class Recorder:
    # Fake module function: remembers the arguments it got and returns a set value
    def __init__(self, result):
        self.result = result
        self.calls = []

    def __call__(self, *args):
        self.calls.append(args[1:])  # skip the client argument
        return self.result


# ---------- Hardware routes (real hardwareDatabase.py) ----------

def test_create_hardware_set(client):
    r = client.post("/create_hardware_set", json={"hwSetName": "HWSet1", "initCapacity": 100})
    assert r.status_code == 201
    assert r.get_json()["success"] is True


def test_create_duplicate_hardware_set(client):
    client.post("/create_hardware_set", json={"hwSetName": "HWSet1", "initCapacity": 100})
    r = client.post("/create_hardware_set", json={"hwSetName": "HWSet1", "initCapacity": 50})
    assert r.status_code == 409


@pytest.mark.parametrize("body", [
    {},                                              # nothing sent
    {"hwSetName": "HWSet1"},                         # no capacity
    {"hwSetName": "HWSet1", "initCapacity": -5},     # negative
    {"hwSetName": "HWSet1", "initCapacity": "abc"},  # not a number
])
def test_create_hardware_set_bad_input(client, body):
    r = client.post("/create_hardware_set", json=body)
    assert r.status_code == 400


def test_get_hw_info(client):
    client.post("/create_hardware_set", json={"hwSetName": "HWSet1", "initCapacity": 100})
    r = client.post("/get_hw_info", json={"hwSetName": "HWSet1"})
    data = r.get_json()
    assert r.status_code == 200
    assert data["capacity"] == 100
    assert data["availability"] == 100


def test_get_hw_info_missing(client):
    r = client.post("/get_hw_info", json={"hwSetName": "Nope"})
    assert r.status_code == 404


def test_get_all_hw_names(client):
    client.post("/create_hardware_set", json={"hwSetName": "HWSet1", "initCapacity": 100})
    client.post("/create_hardware_set", json={"hwSetName": "HWSet2", "initCapacity": 50})
    r = client.post("/get_all_hw_names")
    assert r.status_code == 200
    assert sorted(r.get_json()["hwNames"]) == ["HWSet1", "HWSet2"]


def test_get_all_hw_names_empty(client):
    r = client.post("/get_all_hw_names")
    assert r.get_json()["hwNames"] == []


# ---------- hardwareDatabase.py functions directly ----------

def test_request_space(db_client):
    import hardwareDatabase as hw
    hw.createHardwareSet(db_client, "HWSet1", 10)
    assert hw.requestSpace(db_client, "HWSet1", 4) is True
    assert hw.queryHardwareSet(db_client, "HWSet1")["availability"] == 6


def test_request_space_too_much(db_client):
    import hardwareDatabase as hw
    hw.createHardwareSet(db_client, "HWSet1", 10)
    assert hw.requestSpace(db_client, "HWSet1", 11) is False
    # Availability must not change on a rejected request
    assert hw.queryHardwareSet(db_client, "HWSet1")["availability"] == 10


def test_update_availability_limits(db_client):
    import hardwareDatabase as hw
    hw.createHardwareSet(db_client, "HWSet1", 10)
    assert hw.updateAvailability(db_client, "HWSet1", 5) is True
    assert hw.updateAvailability(db_client, "HWSet1", 11) is False   # above capacity
    assert hw.updateAvailability(db_client, "HWSet1", -1) is False   # negative
    assert hw.updateAvailability(db_client, "Nope", 1) is False      # missing set


# ---------- User routes (fake usersDB) ----------

def test_add_user_hashes_userId(client, monkeypatch):
    fake = Recorder(True)
    monkeypatch.setattr(app_module.usersDB, "addUser", fake)
    r = client.post("/add_user", json={"username": "jake", "userId": "jb123", "password": "pw"})
    assert r.status_code == 201
    # The database layer should get the hashed id, never the raw one
    username, userId, password = fake.calls[0]
    assert userId == protect_user_id("jb123")
    assert userId != "jb123"


def test_add_user_taken(client, monkeypatch):
    monkeypatch.setattr(app_module.usersDB, "addUser", Recorder(False))
    r = client.post("/add_user", json={"username": "jake", "userId": "jb123", "password": "pw"})
    assert r.status_code == 409


def test_add_user_missing_fields(client):
    r = client.post("/add_user", json={"username": "jake"})
    assert r.status_code == 400


def test_login_success(client, monkeypatch):
    monkeypatch.setattr(app_module.usersDB, "login", Recorder(True))
    r = client.post("/login", json={"username": "jake", "userId": "jb123", "password": "pw"})
    assert r.status_code == 200
    # The response gives back the plain userId for the front end
    assert r.get_json()["userId"] == "jb123"


def test_login_wrong_password(client, monkeypatch):
    monkeypatch.setattr(app_module.usersDB, "login", Recorder(False))
    r = client.post("/login", json={"username": "jake", "userId": "jb123", "password": "bad"})
    assert r.status_code == 401


def test_main_page(client, monkeypatch):
    monkeypatch.setattr(app_module.usersDB, "getUserProjectsList", Recorder(["P1"]))
    r = client.get("/main?userId=jb123")
    assert r.status_code == 200
    assert r.get_json()["projects"] == ["P1"]


def test_get_user_projects_unknown_user(client, monkeypatch):
    monkeypatch.setattr(app_module.usersDB, "getUserProjectsList", Recorder(None))
    r = client.post("/get_user_projects_list", json={"userId": "ghost"})
    assert r.status_code == 404


def test_join_project(client, monkeypatch):
    fake = Recorder(True)
    monkeypatch.setattr(app_module.usersDB, "joinProject", fake)
    r = client.post("/join_project", json={"userId": "jb123", "projectId": "P1"})
    assert r.status_code == 200
    assert fake.calls[0] == (protect_user_id("jb123"), "P1")


# ---------- Project routes (fake projectsDB) ----------

def test_create_project_adds_creator(client, monkeypatch):
    monkeypatch.setattr(app_module.projectsDB, "createProject", Recorder(True))
    join = Recorder(True)
    monkeypatch.setattr(app_module.usersDB, "joinProject", join)
    r = client.post("/create_project",
                    json={"projectName": "Demo", "projectId": "P1", "userId": "jb123"})
    assert r.status_code == 201
    assert join.calls[0] == (protect_user_id("jb123"), "P1")


def test_create_project_taken(client, monkeypatch):
    monkeypatch.setattr(app_module.projectsDB, "createProject", Recorder(False))
    r = client.post("/create_project", json={"projectName": "Demo", "projectId": "P1"})
    assert r.status_code == 409


def test_get_project_info(client, monkeypatch):
    from bson.objectid import ObjectId
    project = {"_id": ObjectId(), "projectId": "P1", "projectName": "Demo"}
    monkeypatch.setattr(app_module.projectsDB, "queryProject", Recorder(project))
    r = client.post("/get_project_info", json={"projectId": "P1"})
    assert r.status_code == 200
    # ObjectId must be turned into a string or jsonify would crash
    assert isinstance(r.get_json()["project"]["_id"], str)


def test_get_project_info_missing(client, monkeypatch):
    monkeypatch.setattr(app_module.projectsDB, "queryProject", Recorder(None))
    r = client.post("/get_project_info", json={"projectId": "nope"})
    assert r.status_code == 404


# ---------- Check out / check in (fake projectsDB, real hardware) ----------

def test_check_out_returns_availability(client, monkeypatch, db_client):
    import hardwareDatabase as hw
    hw.createHardwareSet(db_client, "HWSet1", 100)

    # Stand-in for projectsDB.checkOutHW that really takes units from the set
    def fake_check_out(c, projectId, hwSetName, qty, userId):
        return hw.requestSpace(c, hwSetName, qty)
    monkeypatch.setattr(app_module.projectsDB, "checkOutHW", fake_check_out)

    r = client.post("/check_out",
                    json={"projectId": "P1", "hwSetName": "HWSet1", "qty": 30, "userId": "jb123"})
    assert r.status_code == 200
    assert r.get_json()["availability"] == 70


def test_check_out_too_many(client, monkeypatch):
    monkeypatch.setattr(app_module.projectsDB, "checkOutHW", Recorder(False))
    r = client.post("/check_out",
                    json={"projectId": "P1", "hwSetName": "HWSet1", "qty": 999, "userId": "jb123"})
    assert r.status_code == 400


@pytest.mark.parametrize("qty", [0, -3, "abc", None])
def test_check_out_bad_qty(client, qty):
    r = client.post("/check_out",
                    json={"projectId": "P1", "hwSetName": "HWSet1", "qty": qty, "userId": "jb123"})
    assert r.status_code == 400


def test_check_in_too_many(client, monkeypatch):
    monkeypatch.setattr(app_module.projectsDB, "checkInHW", Recorder(False))
    r = client.post("/check_in",
                    json={"projectId": "P1", "hwSetName": "HWSet1", "qty": 5, "userId": "jb123"})
    assert r.status_code == 400


def test_check_in_ok(client, monkeypatch):
    fake = Recorder(True)
    monkeypatch.setattr(app_module.projectsDB, "checkInHW", fake)
    r = client.post("/check_in",
                    json={"projectId": "P1", "hwSetName": "HWSet1", "qty": 5, "userId": "jb123"})
    assert r.status_code == 200
    assert fake.calls[0] == ("P1", "HWSet1", 5, protect_user_id("jb123"))


# ---------- Misc ----------

def test_inventory(client, db_client):
    db_client["HardwareCheckout"]["Projects"].insert_one({"projectId": "P1"})
    r = client.get("/api/inventory")
    assert r.status_code == 200
    assert r.get_json()["projects"][0]["projectId"] == "P1"


def test_database_error_returns_500(client, monkeypatch):
    def broken(*args):
        raise RuntimeError("db down")
    monkeypatch.setattr(app_module.hardwareDB, "getAllHwNames", broken)
    r = client.post("/get_all_hw_names")
    assert r.status_code == 500