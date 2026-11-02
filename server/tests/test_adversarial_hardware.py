"""Adversarial / mutation-derived tests for the hardware inventory server.

Each test pins a behavior derived from the intent (capacity is fixed,
available = capacity - checkedOut, strict input validation, per-project
isolation, optimistic-concurrency guards) and fails under a specific
one-line break of the implementation.
"""

import pytest

import app as flask_app_module
import hardwareDatabase as hardwareDB


# --- a client whose collections let a test interleave a competing writer ----


class _RacingCollection:
    def __init__(self, inner, hook, after):
        self._inner = inner
        self._hook = hook
        self._after = after

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def find_one_and_update(self, *args, **kwargs):
        self._hook(self._inner)
        result = self._inner.find_one_and_update(*args, **kwargs)
        if result is None and self._after is not None:
            self._after(self._inner)
        return result


class _RacingDatabase:
    def __init__(self, inner, hook, after):
        self._inner = inner
        self._hook = hook
        self._after = after

    def __getitem__(self, name):
        return _RacingCollection(self._inner[name], self._hook, self._after)


class RacingClient:
    """Calls `hook(collection)` immediately before every find_one_and_update,
    and `after(collection)` when that update matched no document.
    """

    def __init__(self, inner, hook, after=None):
        self._inner = inner
        self._hook = hook
        self._after = after

    def __getitem__(self, name):
        return _RacingDatabase(self._inner[name], self._hook, self._after)

    def close(self):
        pass


def _raw(mongo, projectId, key):
    return mongo[hardwareDB.DB_NAME][hardwareDB.HARDWARE_SETS_COLLECTION].find_one(
        {"projectId": projectId, "hwSetKey": key}
    )


def _bump_checked_out(by):
    def competitor(collection):
        collection.update_one(
            {"projectId": "H1", "hwSetKey": "hwset1"}, {"$inc": {"checkedOut": by}}
        )

    return competitor


def _post(api, path, **fields):
    body = {"projectId": "H1", "userId": "alice", "hwSetName": "HWSet1", "quantity": 1}
    body.update(fields)
    return api.post(path, json=body)


# --- optimistic concurrency: checkout / checkin -----------------------------


def test_checkout_write_is_pinned_to_the_count_it_read(mongo, seed_set):
    """A competing checkout landing between read and write must not be lost."""
    seed_set("H1", "HWSet1", 10)
    fired = []

    def competitor_once(collection):
        if not fired:
            fired.append(True)
            _bump_checked_out(5)(collection)

    racing = RacingClient(mongo, competitor_once)
    result = hardwareDB.checkoutHardware(racing, "H1", "HWSet1", 3, "alice")

    assert result["available"] == 2
    assert _raw(mongo, "H1", "hwset1")["checkedOut"] == 8


def test_checkout_succeeds_in_one_attempt_despite_unrelated_competing_writes(mongo, seed_set):
    """Ample stock: another writer's concurrent change must not fail or retry the call."""
    seed_set("H1", "HWSet1", 20)
    attempts = []

    def competitor_every_time(collection):
        attempts.append(1)
        _bump_checked_out(1)(collection)

    racing = RacingClient(mongo, competitor_every_time)
    result = hardwareDB.checkoutHardware(racing, "H1", "HWSet1", 3, "alice")

    assert len(attempts) == 1
    assert result["available"] == 16
    assert _raw(mongo, "H1", "hwset1")["checkedOut"] == 4


def test_checkout_is_rejected_when_a_competitor_takes_the_units_between_read_and_write(mongo, seed_set):
    seed_set("H1", "HWSet1", 5)
    racing = RacingClient(mongo, _bump_checked_out(5))

    with pytest.raises(hardwareDB.InsufficientStockError) as caught:
        hardwareDB.checkoutHardware(racing, "H1", "HWSet1", 3, "alice")

    assert (caught.value.onHand, caught.value.requested) == (0, 3)
    assert _raw(mongo, "H1", "hwset1")["checkedOut"] == 5  # our write was not applied


def test_checkout_is_retried_when_units_are_freed_after_the_guard_rejected_it(mongo, seed_set):
    seed_set("H1", "HWSet1", 10)
    state = {"first": True}

    def fill_up_once(collection):
        if state["first"]:
            state["first"] = False
            collection.update_one(
                {"projectId": "H1", "hwSetKey": "hwset1"}, {"$set": {"checkedOut": 10}}
            )

    def free_up_after_rejection(collection):
        collection.update_one(
            {"projectId": "H1", "hwSetKey": "hwset1"}, {"$set": {"checkedOut": 0}}
        )

    racing = RacingClient(mongo, fill_up_once, after=free_up_after_rejection)
    result = hardwareDB.checkoutHardware(racing, "H1", "HWSet1", 3, "alice")

    assert result["available"] == 7
    assert _raw(mongo, "H1", "hwset1")["checkedOut"] == 3


def test_checkin_is_unaffected_by_a_competitor_changing_the_project_wide_aggregate(mongo, seed_set):
    """A checkin is gated by what the CALLING user personally holds, not
    the project-wide `checkedOut` total -- so a competing write that only
    touches the aggregate (never this user's own checkedOutBy entry) must
    not block or corrupt this user's legitimate checkin. This replaces a
    prior version of this test that asserted the opposite (an aggregate-
    only race blocking checkin) -- that was pinning the exact bug being
    fixed here: anyone could check in units someone else checked out.
    """
    seed_set("H1", "HWSet1", 10)
    hardwareDB.checkoutHardware(mongo, "H1", "HWSet1", 6, "alice")
    racing = RacingClient(mongo, _bump_checked_out(-5))

    result = hardwareDB.checkinHardware(racing, "H1", "HWSet1", 3, "alice")

    assert result["myCheckedOut"] == 3  # alice: 6 checked out, 3 checked back in
    raw = _raw(mongo, "H1", "hwset1")
    # aggregate: 6 (alice's checkout) - 5 (competitor's phantom bump,
    # unrelated to any real checkedOutBy entry) - 3 (alice's real checkin)
    assert raw["checkedOut"] == -2
    assert next(e for e in raw["checkedOutBy"] if e["userId"] == "alice")["quantity"] == 3


def test_checkin_write_is_pinned_to_the_count_it_read(mongo, seed_set):
    seed_set("H1", "HWSet1", 10)
    hardwareDB.checkoutHardware(mongo, "H1", "HWSet1", 6, "alice")
    fired = []

    def competitor_once(collection):
        if not fired:
            fired.append(True)
            _bump_checked_out(-2)(collection)

    racing = RacingClient(mongo, competitor_once)
    hardwareDB.checkinHardware(racing, "H1", "HWSet1", 1, "alice")

    assert _raw(mongo, "H1", "hwset1")["checkedOut"] == 3


def test_two_concurrent_checkins_by_the_same_user_cannot_drive_their_holding_negative(mongo, seed_set):
    """The race this module's own docstring calls out: two concurrent
    checkins by the SAME user, both reading the same stale `myHolding`,
    must not both apply -- only one may succeed; the other must see the
    live (already-reduced) holding and fail with CheckinExceedsCheckedOutError,
    not silently push this user's entry below zero.
    """
    seed_set("H1", "HWSet1", 10)
    hardwareDB.checkoutHardware(mongo, "H1", "HWSet1", 5, "alice")

    def concurrent_checkin_lands_first(collection):
        # Simulates a second request for the SAME user's checkin-5 winning
        # the race, landing right before this call's own write attempt.
        collection.update_one(
            {"projectId": "H1", "hwSetKey": "hwset1", "checkedOutBy.userId": "alice"},
            {"$inc": {"checkedOut": -5, "checkedOutBy.$.quantity": -5}},
        )

    racing = RacingClient(mongo, concurrent_checkin_lands_first)
    with pytest.raises(hardwareDB.CheckinExceedsCheckedOutError) as caught:
        hardwareDB.checkinHardware(racing, "H1", "HWSet1", 5, "alice")

    assert (caught.value.checkedOut, caught.value.requested) == (0, 5)
    raw = _raw(mongo, "H1", "hwset1")
    assert next(e for e in raw["checkedOutBy"] if e["userId"] == "alice")["quantity"] == 0
    assert raw["checkedOut"] == 0


def test_release_write_is_pinned_to_the_entry_still_being_present(mongo, seed_set):
    """A duplicate release must not decrement reservedQuantity twice."""
    seed_set("H1", "HWSet1", 10)
    reservationId, _ = hardwareDB.addReservation(mongo, "H1", "HWSet1", 4, "alice", "Alice")

    def competing_release(collection):
        collection.update_one(
            {"projectId": "H1", "hwSetKey": "hwset1"},
            {
                "$pull": {"reservations": {"reservationId": reservationId}},
                "$inc": {"reservedQuantity": -4},
            },
        )

    racing = RacingClient(mongo, competing_release)
    with pytest.raises(hardwareDB.ReservationNotFoundError):
        hardwareDB.removeReservation(racing, "H1", reservationId, "alice")

    assert _raw(mongo, "H1", "hwset1")["reservedQuantity"] == 0


# --- input validation --------------------------------------------------------


@pytest.mark.parametrize("path", ["/api/hardware/checkin", "/api/hardware/checkout", "/api/hardware/request"])
@pytest.mark.parametrize("badName", ["", "   ", 5, {"a": 1}, None])
def test_blank_or_non_string_hardware_set_name_is_rejected_with_400(api, seed_set, path, badName):
    seed_set("H1", "HWSet1", 10)

    response = _post(api, path, hwSetName=badName, userName="Alice")

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_input", "field": "hwSetName"}


@pytest.mark.parametrize("path", ["/api/hardware/checkin", "/api/hardware/checkout", "/api/hardware/request"])
@pytest.mark.parametrize(
    "badQuantity",
    [True, False, 0, -1, 1.5, "2", None, 2**31, hardwareDB.MAX_QUANTITY + 1, 2**63, 2**70],
)
def test_non_positive_non_integer_and_boolean_quantities_are_rejected_with_400(
    api, mongo, seed_set, path, badQuantity
):
    seed_set("H1", "HWSet1", 10)

    response = _post(api, path, quantity=badQuantity, userName="Alice")

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_input", "field": "quantity"}
    raw = _raw(mongo, "H1", "hwset1")
    assert raw["checkedOut"] == 0
    assert raw["reservedQuantity"] == 0


@pytest.mark.parametrize("badCapacity", [0, -1, True, 2.5, "3", None, hardwareDB.MAX_QUANTITY + 1, 2**70])
def test_create_hardware_set_rejects_invalid_capacity(mongo, badCapacity):
    with pytest.raises(hardwareDB.InvalidInventoryInput) as caught:
        hardwareDB.createHardwareSet(mongo, "H1", "HWSet1", badCapacity)
    assert str(caught.value) == "capacity"


@pytest.mark.parametrize("badName", ["", "   ", 7, None])
def test_create_hardware_set_rejects_invalid_name(mongo, badName):
    with pytest.raises(hardwareDB.InvalidInventoryInput) as caught:
        hardwareDB.createHardwareSet(mongo, "H1", badName, 5)
    assert str(caught.value) == "hwSetName"


# --- name identity ------------------------------------------------------------


def test_names_differing_by_inner_whitespace_are_distinct_but_runs_collapse(api, seed_set):
    seed_set("H1", "HW Set 1", 5)
    seed_set("H1", "HWSet1", 7)

    sets = api.get("/api/hardware?projectId=H1&userId=alice").get_json()["hardwareSets"]
    assert sorted((s["hwSetName"], s["capacity"]) for s in sets) == [("HW Set 1", 5), ("HWSet1", 7)]

    response = _post(api, "/api/hardware/checkout", hwSetName="  hw   SET  1 ", quantity=2)
    assert response.status_code == 200
    hwSet = response.get_json()["hardwareSet"]
    assert (hwSet["hwSetName"], hwSet["available"]) == ("HW Set 1", 3)


# --- checkin boundary ---------------------------------------------------------


def test_checkin_of_exactly_everything_checked_out_succeeds(api, seed_set):
    seed_set("H1", "HWSet1", 10)
    _post(api, "/api/hardware/checkout", quantity=4)

    response = _post(api, "/api/hardware/checkin", quantity=4)

    assert response.status_code == 200
    hwSet = response.get_json()["hardwareSet"]
    assert (hwSet["capacity"], hwSet["available"]) == (10, 10)


# --- status listing: isolation and order ---------------------------------------


def test_status_lists_only_the_requested_projects_sets(api, mongo, seed_set):
    mongo[hardwareDB.DB_NAME][hardwareDB.PROJECTS_COLLECTION].insert_one(
        {"householdId": "H2", "users": ["carol"]}
    )
    seed_set("H1", "HWSet1", 10)
    seed_set("H2", "SecretSet", 99)

    sets = api.get("/api/hardware?projectId=H1&userId=alice").get_json()["hardwareSets"]

    assert [s["hwSetName"] for s in sets] == ["HWSet1"]


def test_status_is_sorted_ascending_by_normalized_name(api, seed_set):
    for name in ("Bravo", "alpha", "Charlie"):
        seed_set("H1", name, 5)

    sets = api.get("/api/hardware?projectId=H1&userId=alice").get_json()["hardwareSets"]

    assert [s["hwSetName"] for s in sets] == ["alpha", "Bravo", "Charlie"]


# --- authorization is per project ------------------------------------------------


def test_membership_is_checked_against_the_requested_project(api, mongo, seed_set):
    mongo[hardwareDB.DB_NAME][hardwareDB.PROJECTS_COLLECTION].insert_one(
        {"householdId": "H2", "users": ["carol"]}
    )
    seed_set("H1", "HWSet1", 10)
    seed_set("H2", "HWSet1", 3)

    assert api.get("/api/hardware?projectId=H2&userId=carol").status_code == 200
    assert api.get("/api/hardware?projectId=H1&userId=carol").status_code == 403
    assert api.get("/api/hardware?projectId=H2&userId=alice").status_code == 403


def test_release_is_scoped_to_the_project_named_in_the_request(api, mongo, seed_set):
    mongo[hardwareDB.DB_NAME][hardwareDB.PROJECTS_COLLECTION].insert_one(
        {"householdId": "H2", "users": ["alice"]}
    )
    seed_set("H2", "HWSet1", 10)
    reservationId = _post(
        api, "/api/hardware/request", projectId="H2", userName="Alice", quantity=3
    ).get_json()["requestId"]

    response = api.post(
        "/api/hardware/release",
        json={"projectId": "H1", "userId": "alice", "requestId": reservationId},
    )

    assert response.status_code == 404
    raw = _raw(mongo, "H2", "hwset1")
    assert raw["reservedQuantity"] == 3
    assert len(raw["reservations"]) == 1


def test_the_largest_allowed_quantity_is_accepted_everywhere_and_never_overflows(api, mongo, seed_set):
    maximum = hardwareDB.MAX_QUANTITY
    assert maximum == 2**31 - 1  # small enough that summed reservations cannot overflow BSON int64
    seed_set("H1", "HWSet1", maximum)

    assert _post(api, "/api/hardware/request", userName="Alice", quantity=maximum).status_code == 201
    assert _post(api, "/api/hardware/request", userName="Alice", quantity=maximum).status_code == 201
    assert _post(api, "/api/hardware/checkout", quantity=maximum).status_code == 200
    assert _post(api, "/api/hardware/checkin", quantity=maximum).status_code == 200
    assert _raw(mongo, "H1", "hwset1")["reservedQuantity"] == 2 * maximum
