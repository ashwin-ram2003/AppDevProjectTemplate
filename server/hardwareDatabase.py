# Import necessary libraries and modules
import os
import re
import uuid
from datetime import datetime, timezone

from bson.objectid import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

'''
Structure of a Hardware Set entry (collection `HardwareSets`, one document
per project + hwSetKey):

HardwareSet = {
    '_id': ObjectId,
    'projectId': projectId,
    'hwSetKey': normalizeHwSetName(hwSetName),
    'hwSetName': hwSetName,             # display name as last typed (create or rename)
    'active': bool,                     # False = deactivated; a MISSING field reads as active
    'capacity': int,                    # fixed total units; never changed by checkin/checkout
    'checkedOut': int,                  # units currently checked out, project-wide (0..capacity)
    'checkedOutBy': [
        {
            'userId': userId,
            'quantity': int,            # this user's own running total currently checked out
        },
        ...
    ],                                   # at most one entry per userId
    'reservations': [
        {
            'reservationId': str,       # uuid4 hex
            'userId': userId,
            'userName': userName,
            'quantity': int,
            'createdAt': ISO-8601 str,
        },
        ...
    ],
    'reservedQuantity': int,            # maintained sum of reservations
}

This is the generic HaaS resource-management model from the assignment's
Figure 3 mockup: a project owns any number of named hardware sets (e.g.
HWSet1, HWSet2), each showing Capacity / Available, with Request (reserve),
Checkout, and Checkin actions. There is no storage location, no freshness,
and no per-restock batch history -- those were a prior domain-specific
extension that has been removed.

Deactivating a set (setHardwareSetActive) is refused while any units are
checked out, and a deactivated set refuses new checkouts and new requests.
Check-in and releasing an existing request stay available so nobody is
stranded holding units. Reactivating restores normal use. Rename changes
only the labels (hwSetName / hwSetKey); every internal write pins _id or
reservationId, so it is safe at any time.

`available` (capacity - checkedOut) is derived on read and never stored.
Requests (reservations) are a coordination signal only and never reduce it.

`checkedOutBy` is a per-user accountability ledger: Checkout is still drawn
from the shared pool (gated by `checkedOut` against `capacity`, exactly as
before), but Checkin is now gated by what the CALLING user personally holds
in `checkedOutBy`, not the project-wide `checkedOut` total. Without this, any
project member could check in units a completely different member checked
out, which is what the current `checkedOut`-only design actually allowed --
the aggregate guard only prevented checking in more than was checked out
project-wide, never who did the checking out. An array of records (not a
dynamic object keyed by userId) on purpose: userId is arbitrary user input,
and a `.` or a leading `$` in a Mongo field key has special meaning --
exactly the kind of value-vs-key injection risk `reservations` above and
`assertProjectMember` elsewhere in this codebase already avoid by storing
userId as a field *value*, never as a key.

This module holds ONLY the hardware-set store. Project membership lives in
the separate `Projects` collection (Track A owns writes to it); this module
reads nothing from it directly -- that is projectsDatabase's job via
assertProjectMember.
'''

DB_NAME = os.environ.get("MONGODB_DB", "HaaSResourceManager")
HARDWARE_SETS_COLLECTION = "HardwareSets"
PROJECTS_COLLECTION = "Households"

# Upper bound on any single quantity or capacity. MongoDB stores integers as
# at most 64 bits, so an unbounded value (or a running reservedQuantity sum
# of unbounded values) overflows inside the driver and surfaces as a 500.
MAX_QUANTITY = 2**31 - 1

_WHITESPACE_RUN = re.compile(r"\s+")


def _isValidQuantity(value):
    """True for a whole number from 1 to MAX_QUANTITY (booleans excluded)."""
    return not isinstance(value, bool) and isinstance(value, int) and 1 <= value <= MAX_QUANTITY


class InvalidInventoryInput(Exception):
    """Raised when checkin/checkout/request receives an invalid field. Maps to HTTP 400."""


class ItemNotFoundError(Exception):
    """Raised when an operation references a hardware set that does not exist. Maps to HTTP 404."""


class InsufficientStockError(Exception):
    """Raised when a checkout would exceed the hardware set's on-hand capacity.
    Maps to HTTP 409. Carries onHand (capacity read) and requested
    (quantity asked for) so the caller can report both.
    """

    def __init__(self, onHand, requested):
        self.onHand = onHand
        self.requested = requested
        super().__init__(
            "insufficient stock: onHand={} requested={}".format(onHand, requested)
        )


class HardwareSetNameTakenError(Exception):
    """Raised when a rename targets a name another set in the same project
    already uses. Maps to HTTP 409.
    """


class HardwareSetInactiveError(Exception):
    """Raised when a checkout or request targets a deactivated hardware set.
    Maps to HTTP 409.
    """


class HardwareSetInUseError(Exception):
    """Raised when a deactivate is refused because units are still checked
    out. Maps to HTTP 409. Carries checkedOut (the live count).
    """

    def __init__(self, checkedOut):
        self.checkedOut = checkedOut
        super().__init__("hardware set in use: checkedOut={}".format(checkedOut))


# $ne False matches True AND a missing field, so documents written before
# `active` existed behave as active with no migration.
_ACTIVE_GUARD = {"$ne": False}


class CheckinExceedsCheckedOutError(Exception):
    """Raised when a checkin would return more units than are currently
    checked out. Maps to HTTP 409. Carries checkedOut and requested.
    """

    def __init__(self, checkedOut, requested):
        self.checkedOut = checkedOut
        self.requested = requested
        super().__init__(
            "checkin exceeds checked out: checkedOut={} requested={}".format(checkedOut, requested)
        )


class ReservationNotFoundError(Exception):
    """Raised when releaseReservation cannot find an entry with the given
    reservationId at all (as opposed to one that exists but is owned by
    someone else). Maps to HTTP 404.
    """


class ReservationNotOwnedError(Exception):
    """Raised when releaseReservation finds a reservation with the given
    reservationId but it belongs to a different userId -- only the
    creating member can release their own claim. Maps to HTTP 403.
    Defined here (not in projectsDatabase.py) because hardwareDatabase is
    the module that detects the mismatch; projectsDatabase re-exports it
    for the route layer's error-mapping convenience.
    """


def normalizeHwSetName(rawName):
    """Normalize a raw hardware-set name into its hwSetKey.

    Strips leading/trailing whitespace, lowercases, and collapses every
    internal whitespace run to a single space. Exact match only after
    normalization -- no substring/fuzzy matching, unlike the old food-item
    identity resolver. A generic hardware-set name (e.g. "HWSet1") does not
    need loose matching; requiring an exact (case/whitespace-insensitive)
    name keeps checkin/checkout unambiguous.

    Raises:
        ValueError: if rawName is not a string, or normalizes to the empty
            string.
    """
    if not isinstance(rawName, str):
        raise ValueError("hwSetName must be a string")

    normalized = _WHITESPACE_RUN.sub(" ", rawName.strip()).lower()

    if normalized == "":
        raise ValueError("hwSetName must not be blank")

    return normalized


def _ensureHwSetUniqueIndex(collection):
    """Create the unique compound index backing checkinHardware's upsert.

    Without a unique index on (projectId, hwSetKey), Mongo does not
    serialize two concurrent upserts that both target a never-before-seen
    hwSetKey with the same filter -- both can observe "no matching
    document" and both insert, silently splitting one hardware set's
    capacity across two documents. create_index is idempotent (a no-op
    once the index already exists), so calling it here on every
    checkinHardware call is safe and keeps this module self-contained
    without a separate migration step.
    """
    collection.create_index(
        [("projectId", 1), ("hwSetKey", 1)],
        unique=True,
        name="uniq_project_hwSetKey",
    )


def createHardwareSet(client, projectId, rawName, capacity):
    """Create a hardware set with a fixed `capacity` and nothing checked
    out. Idempotent: if the set already exists it is returned unchanged
    (capacity is never overwritten, and an inactive set stays inactive).
    """
    if not _isValidQuantity(capacity):
        raise InvalidInventoryInput("capacity")

    try:
        normalizedName = normalizeHwSetName(rawName)
    except ValueError:
        raise InvalidInventoryInput("hwSetName")

    collection = client[DB_NAME][HARDWARE_SETS_COLLECTION]
    _ensureHwSetUniqueIndex(collection)

    filter_ = {"projectId": projectId, "hwSetKey": normalizedName}
    update = {
        "$setOnInsert": {
            "projectId": projectId,
            "hwSetKey": normalizedName,
            "hwSetName": rawName,
            "active": True,
            "capacity": capacity,
            "checkedOut": 0,
            "checkedOutBy": [],
            "reservations": [],
            "reservedQuantity": 0,
        },
    }

    try:
        doc = collection.find_one_and_update(
            filter_, update, upsert=True, return_document=ReturnDocument.AFTER
        )
    except DuplicateKeyError:
        doc = collection.find_one_and_update(
            filter_, update, upsert=True, return_document=ReturnDocument.AFTER
        )

    return _serializeHardwareSet(doc)


def _resolveExistingHwSetKey(collection, projectId, rawName):
    """Resolve rawName to an existing hardware set's hwSetKey within one
    project via exact normalized-name match. Raises ItemNotFoundError when
    there is no matching hardware set.
    """
    try:
        normalizedName = normalizeHwSetName(rawName)
    except ValueError:
        raise InvalidInventoryInput("hwSetName")

    doc = collection.find_one({"projectId": projectId, "hwSetKey": normalizedName}, {"hwSetKey": 1})
    if doc is None:
        raise ItemNotFoundError(rawName)

    return normalizedName


def _adjustCheckedOut(client, projectId, rawName, quantity, userId, direction):
    """Shared checkin/checkout write. direction=+1 checks out, -1 checks in.

    `capacity` is never touched. Checkout is still gated by the project-wide
    `checkedOut` against `capacity`, as before -- anyone can draw from the
    shared pool. Checkin is gated by what userId personally holds in
    `checkedOutBy`, NOT the project-wide total -- checking in more than you
    personally checked out raises CheckinExceedsCheckedOutError even if the
    project-wide total would allow it (i.e. even if someone else checked out
    enough to cover the difference).

    Every guard is re-applied inside the atomic find_one_and_update's filter
    itself, evaluated against the live document at write time -- not just
    the stale snapshot read at the top of the loop -- so two concurrent
    calls (checkout vs. checkout, checkin vs. checkin, same user or
    different users) can never push `checkedOut` outside 0..capacity or a
    single user's own `checkedOutBy` entry negative. When a write's filter
    doesn't match (another writer changed the live state first), the loop
    re-reads and retries against fresh data rather than failing outright.

    Checkout writes also carry the active guard, so a deactivate landing
    between the read and the write makes the write miss; the loop then
    re-reads and raises HardwareSetInactiveError instead of retrying
    forever. Checkin deliberately has no active guard.
    """
    if not _isValidQuantity(quantity):
        raise InvalidInventoryInput("quantity")
    if not isinstance(userId, str):
        # Same injection-safety reasoning as assertProjectMember/
        # removeReservation: userId lands in a Mongo filter below, and
        # request.get_json() can hand this function anything JSON allows.
        raise InvalidInventoryInput("userId")

    collection = client[DB_NAME][HARDWARE_SETS_COLLECTION]
    targetKey = _resolveExistingHwSetKey(collection, projectId, rawName)

    while True:
        doc = collection.find_one({"projectId": projectId, "hwSetKey": targetKey})
        if doc is None:
            raise ItemNotFoundError(rawName)

        if direction > 0 and doc.get("active", True) is False:
            raise HardwareSetInactiveError(rawName)

        # capacity never changes after creation, so a stale read of it is safe.
        capacity = doc.get("capacity", 0)
        checkedOut = doc.get("checkedOut", 0)
        myEntry = next(
            (entry for entry in doc.get("checkedOutBy", []) if entry.get("userId") == userId),
            None,
        )
        myHolding = myEntry.get("quantity", 0) if myEntry is not None else 0

        if direction > 0:
            if quantity > capacity - checkedOut:
                raise InsufficientStockError(onHand=capacity - checkedOut, requested=quantity)
            aggregateGuard = {"$lte": capacity - quantity}
        else:
            # Gated by what THIS user holds -- not the project-wide total.
            if quantity > myHolding:
                raise CheckinExceedsCheckedOutError(checkedOut=myHolding, requested=quantity)

        if myEntry is not None:
            # This user already has a checkedOutBy entry -- increment it
            # (checkout) or decrement it (checkin) in place.
            if direction > 0:
                # Checkout still needs the live capacity guard -- that's a
                # real, user-independent limit.
                filter_ = {
                    "_id": doc["_id"],
                    "checkedOut": aggregateGuard,
                    "checkedOutBy.userId": userId,
                    "active": _ACTIVE_GUARD,
                }
            else:
                # Checkin needs no live check on the project-wide
                # `checkedOut` at all -- it can never fall below any one
                # user's own entry, since every write updates both
                # together, so re-checking the LIVE checkedOutBy entry
                # here is already necessary and sufficient. $elemMatch
                # (not just arrayFilters on the update) is what makes this
                # atomic against a second concurrent checkin by the same
                # user: it re-evaluates "quantity currently held >=
                # quantity requested" against the live array element at
                # write time, not the stale myHolding read above. Without
                # it, two concurrent checkins could both pass that stale
                # read and both apply, driving this one user's entry
                # negative.
                filter_ = {
                    "_id": doc["_id"],
                    "checkedOutBy": {
                        "$elemMatch": {"userId": userId, "quantity": {"$gte": quantity}}
                    },
                }
            # The classic single positional operator ($, not $[elem]/
            # arrayFilters) updates whichever array element matched the
            # filter above -- same atomicity guarantee, older and more
            # widely supported syntax (arrayFilters trips a bug in the
            # mongomock version this project tests against).
            updated = collection.find_one_and_update(
                filter_,
                {
                    "$inc": {
                        "checkedOut": direction * quantity,
                        "checkedOutBy.$.quantity": direction * quantity,
                    },
                },
                return_document=ReturnDocument.AFTER,
            )
        else:
            # No existing entry for this user -- only reachable for
            # direction > 0 (checkout): a checkin with myHolding == 0
            # already raised above, since quantity is always >= 1.
            updated = collection.find_one_and_update(
                {
                    "_id": doc["_id"],
                    "checkedOut": aggregateGuard,
                    "checkedOutBy.userId": {"$ne": userId},
                    "active": _ACTIVE_GUARD,
                },
                {
                    "$inc": {"checkedOut": direction * quantity},
                    "$push": {"checkedOutBy": {"userId": userId, "quantity": quantity}},
                },
                return_document=ReturnDocument.AFTER,
            )

        if updated is not None:
            return _serializeHardwareSet(updated, userId)


def renameHardwareSet(client, projectId, rawName, rawNewName, userId=None):
    """Rename a hardware set: hwSetName (display, stripped of surrounding
    whitespace) and hwSetKey change together. The unique index is the only
    collision check, so two racing renames cannot both win. Raises
    HardwareSetNameTakenError on a collision, ItemNotFoundError if the set
    does not exist.
    """
    try:
        currentKey = normalizeHwSetName(rawName)
    except ValueError:
        raise InvalidInventoryInput("hwSetName")
    try:
        newKey = normalizeHwSetName(rawNewName)
    except ValueError:
        raise InvalidInventoryInput("newName")

    collection = client[DB_NAME][HARDWARE_SETS_COLLECTION]
    # Otherwise only createHardwareSet makes this index, and without it the
    # collision would silently be allowed.
    _ensureHwSetUniqueIndex(collection)

    try:
        updated = collection.find_one_and_update(
            {"projectId": projectId, "hwSetKey": currentKey},
            {"$set": {"hwSetKey": newKey, "hwSetName": rawNewName.strip()}},
            return_document=ReturnDocument.AFTER,
        )
    except DuplicateKeyError:
        raise HardwareSetNameTakenError(rawNewName)

    if updated is None:
        raise ItemNotFoundError(rawName)

    return _serializeHardwareSet(updated, userId)


def setHardwareSetActive(client, projectId, rawName, active, userId=None):
    """Deactivate (active=False) or reactivate (active=True) a hardware set.
    Both are idempotent. Deactivating is refused with HardwareSetInUseError
    while any units are checked out.
    """
    if not isinstance(active, bool):
        raise InvalidInventoryInput("active")
    try:
        key = normalizeHwSetName(rawName)
    except ValueError:
        raise InvalidInventoryInput("hwSetName")

    collection = client[DB_NAME][HARDWARE_SETS_COLLECTION]
    base = {"projectId": projectId, "hwSetKey": key}

    if active:
        updated = collection.find_one_and_update(
            base, {"$set": {"active": True}}, return_document=ReturnDocument.AFTER
        )
        if updated is None:
            raise ItemNotFoundError(rawName)
        return _serializeHardwareSet(updated, userId)

    while True:
        # $not $gt (not a literal 0): a document missing checkedOut must
        # still match, or the re-read below would loop forever.
        updated = collection.find_one_and_update(
            dict(base, checkedOut={"$not": {"$gt": 0}}),
            {"$set": {"active": False}},
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return _serializeHardwareSet(updated, userId)

        doc = collection.find_one(base)
        if doc is None:
            raise ItemNotFoundError(rawName)
        if doc.get("checkedOut", 0) > 0:
            raise HardwareSetInUseError(doc.get("checkedOut", 0))
        # A concurrent check-in emptied the set; try the write again.


def checkinHardware(client, projectId, rawName, quantity, userId):
    """Check in (return) `quantity` units userId personally checked out,
    raising availability. Raises CheckinExceedsCheckedOutError if userId
    doesn't personally hold that many units -- even if the project-wide
    total checked out would otherwise allow it.
    """
    return _adjustCheckedOut(client, projectId, rawName, quantity, userId, -1)


def checkoutHardware(client, projectId, rawName, quantity, userId):
    """Check out `quantity` units, lowering availability and crediting them
    to userId's own `checkedOutBy` entry. Raises InsufficientStockError
    (onHand = current availability) if more than are available. Outstanding
    requests never gate checkout.
    """
    return _adjustCheckedOut(client, projectId, rawName, quantity, userId, +1)


def addReservation(client, projectId, rawName, quantity, userId, userName):
    """Append a reservation entry (a "Request", per SN3) to the hardware set
    and increment reservedQuantity.

    Never compares quantity against capacity -- requesting beyond what is
    on hand is a legitimate thing for a project member to do; the
    overbooking guard applies to checkout only. Uses a single $push/$inc
    update so two simultaneous requests both survive rather than one
    overwriting the other.
    """
    if not _isValidQuantity(quantity):
        raise InvalidInventoryInput("quantity")

    # userName is stored directly into the reservation entry and echoed
    # back in API responses; reject anything but a string (or omitted)
    # rather than persisting a JSON object/array (defense-in-depth
    # alongside the projectId/userId/reservationId checks).
    if userName is not None and not isinstance(userName, str):
        raise InvalidInventoryInput("userName")

    db = client[DB_NAME]
    collection = db[HARDWARE_SETS_COLLECTION]

    targetKey = _resolveExistingHwSetKey(collection, projectId, rawName)

    reservationId = uuid.uuid4().hex
    reservation = {
        "reservationId": reservationId,
        "userId": userId,
        "userName": userName,
        "quantity": quantity,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }

    updated = collection.find_one_and_update(
        {"projectId": projectId, "hwSetKey": targetKey, "active": _ACTIVE_GUARD},
        {
            "$push": {"reservations": reservation},
            "$inc": {"reservedQuantity": quantity},
        },
        return_document=ReturnDocument.AFTER,
    )

    if updated is None:
        # Either the set vanished or the active guard missed.
        if collection.find_one({"projectId": projectId, "hwSetKey": targetKey}, {"_id": 1}) is None:
            raise ItemNotFoundError(rawName)
        raise HardwareSetInactiveError(rawName)

    return reservationId, _serializeHardwareSet(updated, userId)


def removeReservation(client, projectId, reservationId, userId):
    """Pull the reservation entry matching BOTH reservationId and userId,
    decrementing reservedQuantity by that entry's own quantity.

    When nothing is pulled, re-reads to distinguish the two failure
    cases: an entry with that reservationId owned by someone else raises
    ReservationNotOwnedError (403); no such entry at all raises
    ReservationNotFoundError (404).
    """
    # reservationId is used directly in a Mongo filter below; without this
    # check a dict/list value (request.get_json() decodes arbitrary JSON)
    # could be interpreted as a query operator instead of an equality
    # match. Treat a non-string reservationId the same as one that simply
    # doesn't exist.
    if not isinstance(reservationId, str):
        raise ReservationNotFoundError(reservationId)

    db = client[DB_NAME]
    collection = db[HARDWARE_SETS_COLLECTION]

    doc = collection.find_one(
        {"projectId": projectId, "reservations.reservationId": reservationId}
    )

    if doc is None:
        raise ReservationNotFoundError(reservationId)

    entry = next(
        (
            reservation
            for reservation in doc.get("reservations", [])
            if reservation.get("reservationId") == reservationId
        ),
        None,
    )
    if entry is None:
        raise ReservationNotFoundError(reservationId)

    if entry.get("userId") != userId:
        raise ReservationNotOwnedError(reservationId)

    # Pin the write on the reservation still being present in the array,
    # not just on _id. Without this, a duplicate/concurrent release for
    # the same reservationId (e.g. a second browser tab, or a client
    # retry after a dropped response) can pass the ownership check above
    # twice -- each request reads its own copy of `entry` before either
    # writes -- and then both execute this update. The $pull is already
    # idempotent (a second pull matching nothing is a no-op), but without
    # this filter the $inc is unconditional and fires twice for one
    # logical release, double-decrementing reservedQuantity.
    updated = collection.find_one_and_update(
        {"_id": doc["_id"], "reservations.reservationId": reservationId},
        {
            "$pull": {"reservations": {"reservationId": reservationId}},
            "$inc": {"reservedQuantity": -entry.get("quantity", 0)},
        },
        return_document=ReturnDocument.AFTER,
    )

    if updated is None:
        # A losing duplicate/concurrent call: the reservation was already
        # pulled by the winning call between our read and this write.
        # Same outward result as "already released" (404), matching the
        # existing sequential double-release contract.
        raise ReservationNotFoundError(reservationId)

    return _serializeHardwareSet(updated, userId)


def getHardwareStatus(client, projectId, userId=None):
    """Return a list of hardware-set dicts for the project, sorted by
    display name for deterministic, repeatable ordering.

    userId, when given, is whose personal `myCheckedOut` figure to include
    in each dict -- see _serializeHardwareSet. None (e.g. no acting user in
    context) simply omits it.
    """
    db = client[DB_NAME]
    collection = db[HARDWARE_SETS_COLLECTION]

    items = [
        _serializeHardwareSet(doc, userId) for doc in collection.find({"projectId": projectId})
    ]
    items.sort(key=lambda item: item.get("hwSetKey", ""))
    return items


def _serializeHardwareSet(doc, userId=None):
    """Convert a raw Mongo document into a JSON-serializable hardware-set
    dict with `available` and `myCheckedOut` derived.

    The API boundary uses "request"/"requestId"/"requestedQuantity"/
    "available" (the assignment mockup's own Figure 3 vocabulary) even
    though the internal storage/implementation below this line keeps its
    original "reservation"/"availability" naming -- only this serializer
    and the /api/hardware/request+release routes in app.py know about the
    translation, so client and server agree on the wire format without a
    repo-wide rename of the underlying reservation machinery.

    `myCheckedOut` is userId's own entry in `checkedOutBy` (0 if userId is
    None, or has no entry) -- the number the client should actually cap a
    Check In control at, not the project-wide `available`/`checkedOut`
    figures, which say nothing about who personally holds what.
    """
    capacity = doc.get("capacity", 0)
    checkedOut = doc.get("checkedOut", 0)
    reservedQuantity = doc.get("reservedQuantity", 0)
    requests = [
        {
            "requestId": reservation.get("reservationId"),
            "userId": reservation.get("userId"),
            "userName": reservation.get("userName"),
            "quantity": reservation.get("quantity"),
            "createdAt": reservation.get("createdAt"),
        }
        for reservation in doc.get("reservations", [])
    ]
    myEntry = next(
        (entry for entry in doc.get("checkedOutBy", []) if entry.get("userId") == userId),
        None,
    )

    return {
        "_id": str(doc["_id"]) if isinstance(doc.get("_id"), ObjectId) else doc.get("_id"),
        "projectId": doc.get("projectId"),
        "hwSetKey": doc.get("hwSetKey"),
        "hwSetName": doc.get("hwSetName"),
        "active": doc.get("active", True),
        "capacity": capacity,
        "requests": requests,
        "requestedQuantity": reservedQuantity,
        "available": max(capacity - checkedOut, 0),
        "myCheckedOut": myEntry.get("quantity", 0) if myEntry is not None else 0,
    }
