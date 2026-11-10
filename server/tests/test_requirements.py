import pytest

import app as server
from encryption import protect_user_id
from conftest import make_user, login


# ---------- helpers ----------

def create_project(c, projectId="p1", name="Demo", description="test project"):
    return c.post("/create_project",
                  json={"projectName": name, "projectId": projectId, "description": description})


def check_out(c, hwSetName, qty, projectId="p1"):
    return c.post("/check_out", json={"projectId": projectId, "hwSetName": hwSetName, "qty": qty})


def check_in(c, hwSetName, qty, projectId="p1"):
    return c.post("/check_in", json={"projectId": projectId, "hwSetName": hwSetName, "qty": qty})


def hw(c, hwSetName):
    return c.post("/get_hw_info", json={"hwSetName": hwSetName}).get_json()


def project_usage(c, projectId="p1"):
    return c.post("/get_project_info", json={"projectId": projectId}).get_json()["project"]["hwSets"]



# Sign up as a new user
def test_01_sign_up_new_user(api):
    r = api.post("/add_user", json={"username": "Alice", "userId": "alice1", "password": "pw123"})
    assert r.status_code == 201
    assert r.get_json()["success"] is True


def test_01_sign_up_duplicate_user_id(api):
    make_user(api, "alice1")
    r = api.post("/add_user", json={"username": "Bob", "userId": "alice1", "password": "other"})
    assert r.status_code == 409


@pytest.mark.parametrize("body", [
    {"userId": "a1", "password": "pw"},
    {"username": "A", "password": "pw"},
    {"username": "A", "userId": "a1"},
])
def test_01_sign_up_missing_fields(api, body):
    assert api.post("/add_user", json=body).status_code == 400


def test_01_userid_and_password_are_encrypted(api):
    # Spec: "Security features to encrypt the userid and password"
    make_user(api, "alice1", password="pw123")
    users = server.client["Users"]["users"]
    assert users.find_one({"userId": "alice1"}) is None
    doc = users.find_one({"userId": protect_user_id("alice1")})
    assert doc is not None
    assert doc["password"] != "pw123"


# ---------- 2. Sign in with correct userId/password ----------

def test_02_sign_in_correct(api):
    make_user(api, "alice1")
    r = login(api, "alice1")
    assert r.status_code == 200
    assert r.get_json()["success"] is True
    assert api.get("/main").status_code == 200   # session works on a protected route


# ---------- 3. Sign in with a wrong combination ----------

@pytest.mark.parametrize("userId,password", [
    ("alice1", "wrongpw"),
    ("nobody", "pw123"),
    ("ALICE1", "pw123"),
])
def test_03_sign_in_wrong(api, userId, password):
    make_user(api, "alice1")
    r = login(api, userId, password)
    assert r.status_code == 401
    assert api.get("/main").status_code == 401   # no session created


# ---------- 4. Create a new project ----------

def test_04_create_new_project(logged_in):
    r = create_project(logged_in)
    assert r.status_code == 201

    owned = logged_in.post("/get_user_projects", json={}).get_json()["owned"]
    assert [p["projectId"] for p in owned] == ["p1"]
    assert owned[0]["projectName"] == "Demo"
    assert owned[0]["description"] == "test project"


def test_04_create_project_requires_login(api):
    assert create_project(api).status_code == 401


def test_04_create_project_missing_fields(logged_in):
    r = logged_in.post("/create_project", json={"projectName": "Demo"})
    assert r.status_code == 400


# ---------- 5. Create a project with an existing ID ----------

def test_05_create_project_duplicate_id(logged_in):
    create_project(logged_in)
    assert create_project(logged_in, name="Other").status_code == 409


# ---------- 6. Join an existing project ----------

def test_06_join_existing_project(logged_in, second_client):
    create_project(logged_in)
    make_user(second_client, "bob1")
    login(second_client, "bob1")

    r = second_client.post("/join_project", json={"projectId": "p1"})
    assert r.status_code == 200
    shared = second_client.post("/get_user_projects", json={}).get_json()["shared"]
    assert [p["projectId"] for p in shared] == ["p1"]


def test_06_join_missing_project(logged_in):
    assert logged_in.post("/join_project", json={"projectId": "nope"}).status_code == 400


def test_06_join_twice_rejected(logged_in):
    create_project(logged_in)   # creator is already a member
    assert logged_in.post("/join_project", json={"projectId": "p1"}).status_code == 400


# ---------- Resource display (spec: capacity and availability of HWSet1/HWSet2) ----------

def test_hardware_sets_listed_and_show_capacity(logged_in):
    names = logged_in.post("/get_all_hw_names", json={}).get_json()["hwNames"]
    assert set(names) >= {"HWSet1", "HWSet2"}
    for name in ("HWSet1", "HWSet2"):
        info = hw(logged_in, name)
        assert info["capacity"] == 100
        assert info["availability"] == 100


def test_unknown_hardware_set(logged_in):
    r = logged_in.post("/get_hw_info", json={"hwSetName": "HWSet9"})
    assert r.status_code == 404


# ---------- 7-9. Check out HWSet1 and HWSet2, availability drops ----------

def test_07_to_09_checkout_reduces_availability(logged_in):
    create_project(logged_in)

    r1 = check_out(logged_in, "HWSet1", 20)
    assert r1.status_code == 200
    assert r1.get_json()["availability"] == 80

    r2 = check_out(logged_in, "HWSet2", 30)
    assert r2.status_code == 200
    assert r2.get_json()["availability"] == 70

    assert hw(logged_in, "HWSet1")["availability"] == 80
    assert hw(logged_in, "HWSet2")["availability"] == 70
    assert hw(logged_in, "HWSet1")["capacity"] == 100   # capacity never changes
    assert project_usage(logged_in) == {"HWSet1": 20, "HWSet2": 30}


# ---------- 10. Check out more than available ----------

def test_10_checkout_more_than_available(logged_in):
    create_project(logged_in)
    check_out(logged_in, "HWSet1", 90)

    r = check_out(logged_in, "HWSet1", 11)
    assert r.status_code == 400
    assert r.get_json()["availability"] == 10      # unchanged
    assert project_usage(logged_in) == {"HWSet1": 90}


@pytest.mark.parametrize("qty", [
    0, -5, "abc", None,
    # parse_qty() in app.py uses int(), which turns 1.5 into 1 instead of rejecting it
    pytest.param(1.5, marks=pytest.mark.xfail(reason="parse_qty truncates decimals", strict=True)),
])
def test_10_checkout_invalid_qty(logged_in, qty):
    create_project(logged_in)
    assert check_out(logged_in, "HWSet1", qty).status_code == 400
    assert hw(logged_in, "HWSet1")["availability"] == 100


# ---------- 11-12. Check in HWSet1, availability rises ----------

def test_11_12_checkin_increases_availability(logged_in):
    create_project(logged_in)
    check_out(logged_in, "HWSet1", 20)

    r = check_in(logged_in, "HWSet1", 1)
    assert r.status_code == 200
    assert r.get_json()["availability"] == 81
    assert project_usage(logged_in)["HWSet1"] == 19


def test_11_checkin_more_than_checked_out(logged_in):
    create_project(logged_in)
    check_out(logged_in, "HWSet1", 5)

    r = check_in(logged_in, "HWSet1", 6)
    assert r.status_code == 400
    assert hw(logged_in, "HWSet1")["availability"] == 95
    assert project_usage(logged_in)["HWSet1"] == 5


def test_11_checkin_never_exceeds_capacity(logged_in):
    create_project(logged_in)
    assert check_in(logged_in, "HWSet1", 1).status_code == 400
    assert hw(logged_in, "HWSet1")["availability"] == 100


# ---------- 13. Log off ----------

def test_13_logout_blocks_protected_routes(logged_in):
    assert logged_in.post("/logout").status_code == 200
    assert logged_in.get("/main").status_code == 401
    assert check_out(logged_in, "HWSet1", 1).status_code == 401


# ---------- 14. Log in again, state persists ----------

def test_14_state_persists_after_relogin(logged_in):
    create_project(logged_in)
    check_out(logged_in, "HWSet1", 20)
    check_out(logged_in, "HWSet2", 30)
    check_in(logged_in, "HWSet1", 1)
    logged_in.post("/logout")

    login(logged_in, "alice1")
    owned = logged_in.post("/get_user_projects", json={}).get_json()["owned"]
    assert [p["projectId"] for p in owned] == ["p1"]
    assert project_usage(logged_in) == {"HWSet1": 19, "HWSet2": 30}
    assert hw(logged_in, "HWSet1")["availability"] == 81
    assert hw(logged_in, "HWSet2")["availability"] == 70


# ---------- 15-20. TA account: create, login, authorization, shared check-in ----------

@pytest.fixture
def alice_with_hardware(logged_in):
    """Steps 1-12: Alice owns p1 with 19 x HWSet1 and 30 x HWSet2 checked out."""
    create_project(logged_in)
    check_out(logged_in, "HWSet1", 20)
    check_out(logged_in, "HWSet2", 30)
    check_in(logged_in, "HWSet1", 1)
    return logged_in


@pytest.fixture
def ta(second_client):
    make_user(second_client, "ta1", password="tapw", username="TA")
    assert login(second_client, "ta1", "tapw").status_code == 200   # step 15
    return second_client


def test_16_ta_cannot_create_existing_project_id(alice_with_hardware, ta):
    assert create_project(ta, name="TA copy").status_code == 409


def test_17_non_member_is_denied(alice_with_hardware, ta):
    # Before joining, the TA can't see or use Alice's project
    assert ta.post("/get_project_info", json={"projectId": "p1"}).status_code == 403
    assert check_out(ta, "HWSet1", 1).status_code == 400
    assert check_in(ta, "HWSet2", 1).status_code == 400
    assert hw(ta, "HWSet1")["availability"] == 81   # nothing changed


def test_17_member_is_allowed_after_join(alice_with_hardware, ta):
    assert ta.post("/join_project", json={"projectId": "p1"}).status_code == 200
    assert ta.post("/get_project_info", json={"projectId": "p1"}).status_code == 200


def test_18_19_ta_checks_in_hardware_alice_checked_out(alice_with_hardware, ta):
    ta.post("/join_project", json={"projectId": "p1"})

    r = check_in(ta, "HWSet2", 10)
    assert r.status_code == 200
    assert r.get_json()["availability"] == 80     # 70 -> 80
    assert project_usage(ta)["HWSet2"] == 20


def test_20_ta_checks_out_hardware(alice_with_hardware, ta):
    ta.post("/join_project", json={"projectId": "p1"})

    r = check_out(ta, "HWSet1", 5)
    assert r.status_code == 200
    assert r.get_json()["availability"] == 76     # 81 -> 76
    assert project_usage(ta)["HWSet1"] == 24

    # Alice sees the TA's change on the shared project
    assert project_usage(alice_with_hardware)["HWSet1"] == 24