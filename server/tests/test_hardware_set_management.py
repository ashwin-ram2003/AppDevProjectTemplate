"""Rename, deactivate/reactivate, legacy-document and race coverage for
hardware-set management (US-14 / STRETCH-02)."""

import pytest

import hardwareDatabase as hardwareDB
from test_adversarial_hardware import RacingClient


def _coll(mongo):
    return mongo[hardwareDB.DB_NAME][hardwareDB.HARDWARE_SETS_COLLECTION]


def _raw(mongo, projectId, key):
    return _coll(mongo).find_one({"projectId": projectId, "hwSetKey": key})


def _body(**fields):
    body = {"projectId": "H1", "userId": "alice", "hwSetName": "HWSet1"}
    body.update(fields)
    return body


def _rename(api, newName, **fields):
    return api.post("/api/hardware/rename", json=_body(newName=newName, **fields))


def _set_active(api, active, **fields):
    return api.post("/api/hardware/set_active", json=_body(active=active, **fields))


def _checkout(api, quantity=1, **fields):
    return api.post("/api/hardware/checkout", json=_body(quantity=quantity, **fields))


def _request(api, quantity=1, **fields):
    return api.post(
        "/api/hardware/request", json=_body(quantity=quantity, userName="Alice", **fields)
    )


@pytest.fixture
def stocked(mongo, seed_set):
    seed_set("H1", "HWSet1", 10)
    return mongo


# ------------------------------------------------------------------ rename


def test_rename_success_changes_name_and_key(api, stocked):
    before = _raw(stocked, "H1", "hwset1")
    hardwareDB.checkoutHardware(stocked, "H1", "HWSet1", 4, "alice")
    res = _rename(api, "Widgets")
    assert res.status_code == 200
    hw = res.get_json()["hardwareSet"]
    assert hw["hwSetName"] == "Widgets"
    assert hw["hwSetKey"] == "widgets"
    assert hw["myCheckedOut"] == 4
    after = _raw(stocked, "H1", "widgets")
    assert after["_id"] == before["_id"]
    assert after["capacity"] == 10 and after["checkedOut"] == 4
    assert _raw(stocked, "H1", "hwset1") is None
    assert _checkout(api).status_code == 404


def test_rename_case_only_changes_display_name_only(api, stocked):
    res = _rename(api, "HWSET1")
    assert res.status_code == 200
    doc = _raw(stocked, "H1", "hwset1")
    assert doc["hwSetName"] == "HWSET1"


def test_rename_spacing_only_and_strips_whitespace(api, stocked):
    res = _rename(api, "  HWSet1  ")
    assert res.status_code == 200
    assert _raw(stocked, "H1", "hwset1")["hwSetName"] == "HWSet1"
    res = _rename(api, "  My   Set  ")
    assert res.status_code == 200
    assert _raw(stocked, "H1", "my set")["hwSetName"] == "My   Set"


def test_rename_collision_is_409_and_changes_nothing(api, stocked, seed_set):
    seed_set("H1", "Other", 5)
    before = sorted(_coll(stocked).find({}, {"_id": 0}), key=lambda d: d["hwSetKey"])
    res = _rename(api, "OTHER")
    assert res.status_code == 409
    assert res.get_json() == {"error": "hardware_set_name_taken", "field": "newName"}
    after = sorted(_coll(stocked).find({}, {"_id": 0}), key=lambda d: d["hwSetKey"])
    assert before == after


def test_rename_same_name_in_other_project_is_not_collision(api, mongo, stocked, seed_set):
    seed_set("H2", "Taken", 5)
    assert _rename(api, "Taken").status_code == 200


def test_rename_missing_set_is_404(api, stocked):
    assert _rename(api, "X", hwSetName="Nope").status_code == 404


@pytest.mark.parametrize("bad", ["", "   ", {"$ne": ""}, 5, ["a"], None])
def test_rename_bad_new_name_is_400(api, stocked, bad):
    res = _rename(api, bad)
    assert res.status_code == 400
    assert res.get_json()["field"] == "newName"


@pytest.mark.parametrize("bad", [{"$ne": ""}, 5, ["a"], None, ""])
def test_rename_bad_current_name_is_400(api, stocked, bad):
    res = _rename(api, "X", hwSetName=bad)
    assert res.status_code == 400
    assert res.get_json()["field"] == "hwSetName"


def test_rename_non_member_is_403_and_writes_nothing(api, stocked):
    before = list(_coll(stocked).find({}))
    res = _rename(api, "Widgets", userId="mallory")
    assert res.status_code == 403
    assert list(_coll(stocked).find({})) == before


def test_rename_race_competing_insert_is_name_taken(mongo, stocked):
    def competitor(collection):
        collection.insert_one(
            {"projectId": "H1", "hwSetKey": "target", "hwSetName": "Target", "capacity": 1}
        )

    racing = RacingClient(mongo, competitor)
    with pytest.raises(hardwareDB.HardwareSetNameTakenError):
        hardwareDB.renameHardwareSet(racing, "H1", "HWSet1", "Target")


def test_rename_collision_without_prior_index(mongo):
    coll = _coll(mongo)
    coll.insert_many(
        [
            {"projectId": "H1", "hwSetKey": "a", "hwSetName": "A", "capacity": 1},
            {"projectId": "H1", "hwSetKey": "b", "hwSetName": "B", "capacity": 1},
        ]
    )
    try:
        coll.drop_index("uniq_project_hwSetKey")
    except Exception:
        pass
    with pytest.raises(hardwareDB.HardwareSetNameTakenError):
        hardwareDB.renameHardwareSet(mongo, "H1", "A", "b")


# -------------------------------------------------- deactivate / reactivate


def test_deactivate_idle_set_and_repeat(api, stocked):
    res = _set_active(api, False)
    assert res.status_code == 200
    assert res.get_json()["hardwareSet"]["active"] is False
    assert _set_active(api, False).status_code == 200


def test_deactivate_with_units_out_is_409_with_count(api, stocked):
    hardwareDB.checkoutHardware(stocked, "H1", "HWSet1", 3, "alice")
    res = _set_active(api, False)
    assert res.status_code == 409
    assert res.get_json() == {"error": "hardware_set_in_use", "checkedOut": 3}
    assert _raw(stocked, "H1", "hwset1").get("active") is True


def test_checkout_on_inactive_is_409_and_writes_nothing(api, stocked):
    hardwareDB.checkoutHardware(stocked, "H1", "HWSet1", 2, "alice")
    hardwareDB.checkinHardware(stocked, "H1", "HWSet1", 2, "alice")
    _set_active(api, False)
    before = _raw(stocked, "H1", "hwset1")
    for user in ("alice", "bob"):
        res = _checkout(api, userId=user)
        assert res.status_code == 409
        assert res.get_json() == {"error": "hardware_set_inactive"}
    assert _raw(stocked, "H1", "hwset1") == before


def test_request_on_inactive_is_409(api, stocked):
    _set_active(api, False)
    res = _request(api)
    assert res.status_code == 409
    assert res.get_json() == {"error": "hardware_set_inactive"}
    doc = _raw(stocked, "H1", "hwset1")
    assert doc["reservedQuantity"] == 0 and doc["reservations"] == []


def test_checkin_and_release_work_while_inactive(api, stocked):
    hardwareDB.checkoutHardware(stocked, "H1", "HWSet1", 3, "alice")
    reservationId = _request(api).get_json()["requestId"]
    _coll(stocked).update_one({"hwSetKey": "hwset1"}, {"$set": {"active": False}})
    res = api.post("/api/hardware/checkin", json=_body(quantity=2))
    assert res.status_code == 200
    res = api.post("/api/hardware/release", json=_body(requestId=reservationId))
    assert res.status_code == 200


def test_reactivate_restores_use_and_is_idempotent(api, stocked):
    _set_active(api, False)
    res = _set_active(api, True)
    assert res.status_code == 200
    assert res.get_json()["hardwareSet"]["active"] is True
    assert _set_active(api, True).status_code == 200
    assert _checkout(api).status_code == 200
    assert _request(api).status_code == 201


def test_set_active_missing_set_and_non_member(api, stocked):
    assert _set_active(api, False, hwSetName="Nope").status_code == 404
    before = list(_coll(stocked).find({}))
    assert _set_active(api, False, userId="mallory").status_code == 403
    assert list(_coll(stocked).find({})) == before


@pytest.mark.parametrize("bad", ["true", 1, 0, None])
def test_set_active_non_boolean_is_400(api, stocked, bad):
    res = _set_active(api, bad)
    assert res.status_code == 400
    assert res.get_json()["field"] == "active"


def test_set_active_missing_field_is_400(api, stocked):
    res = api.post("/api/hardware/set_active", json=_body())
    assert res.status_code == 400
    assert res.get_json()["field"] == "active"


def test_legacy_document_without_active_behaves_as_active(api, stocked):
    _coll(stocked).update_one({"hwSetKey": "hwset1"}, {"$unset": {"active": ""}})
    got = api.get("/api/hardware", query_string={"projectId": "H1", "userId": "alice"})
    assert got.get_json()["hardwareSets"][0]["active"] is True
    assert _checkout(api).status_code == 200
    assert _request(api).status_code == 201
    _coll(stocked).update_one({"hwSetKey": "hwset1"}, {"$unset": {"active": ""}})
    hardwareDB.checkinHardware(stocked, "H1", "HWSet1", 1, "alice")
    assert _set_active(api, False).status_code == 200


def test_create_on_existing_inactive_set_is_unchanged(api, stocked):
    _set_active(api, False)
    res = api.post(
        "/api/hardware/create", json=_body(hwSetName="HWSet1", capacity=99)
    )
    hw = res.get_json()["hardwareSet"]
    assert hw["active"] is False and hw["capacity"] == 10


def test_created_document_stores_active_true(stocked):
    assert _raw(stocked, "H1", "hwset1")["active"] is True


# ------------------------------------------------------------------- races


def _deactivate_hook(collection):
    collection.update_one({"hwSetKey": "hwset1"}, {"$set": {"active": False}})


def test_race_deactivate_before_first_time_checkout(stocked):
    racing = RacingClient(stocked, _deactivate_hook)
    with pytest.raises(hardwareDB.HardwareSetInactiveError):
        hardwareDB.checkoutHardware(racing, "H1", "HWSet1", 1, "alice")
    assert _raw(stocked, "H1", "hwset1")["checkedOut"] == 0


def test_race_deactivate_before_checkout_with_existing_entry(stocked):
    hardwareDB.checkoutHardware(stocked, "H1", "HWSet1", 1, "alice")
    racing = RacingClient(stocked, _deactivate_hook)
    with pytest.raises(hardwareDB.HardwareSetInactiveError):
        hardwareDB.checkoutHardware(racing, "H1", "HWSet1", 1, "alice")
    assert _raw(stocked, "H1", "hwset1")["checkedOut"] == 1


def test_race_deactivate_before_request(stocked):
    racing = RacingClient(stocked, _deactivate_hook)
    with pytest.raises(hardwareDB.HardwareSetInactiveError):
        hardwareDB.addReservation(racing, "H1", "HWSet1", 1, "alice", "Alice")
    doc = _raw(stocked, "H1", "hwset1")
    assert doc["reservedQuantity"] == 0 and doc["reservations"] == []


def test_race_checkout_before_deactivate_is_in_use(stocked):
    def bump(collection):
        collection.update_one({"hwSetKey": "hwset1"}, {"$inc": {"checkedOut": 2}})

    racing = RacingClient(stocked, bump)
    with pytest.raises(hardwareDB.HardwareSetInUseError) as info:
        hardwareDB.setHardwareSetActive(racing, "H1", "HWSet1", False)
    assert info.value.checkedOut == 2
    assert _raw(stocked, "H1", "hwset1")["active"] is True


def test_deactivate_terminates_when_checked_out_field_missing(stocked):
    _coll(stocked).update_one({"hwSetKey": "hwset1"}, {"$unset": {"checkedOut": ""}})
    hw = hardwareDB.setHardwareSetActive(stocked, "H1", "HWSet1", False)
    assert hw["active"] is False
