# Import necessary libraries and modules
import os
import re
import uuid
from datetime import datetime, timezone

from bson.objectid import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from config import DB_NAME

'''
Structure of a Hardware Set entry (collection `HardwareSets`, one document
per project + hwSetKey):

HardwareSet = {
    '_id': ObjectId,
    'projectId': projectId,
    'hwSetKey': normalizeHwSetName(hwSetName),
    'hwSetName': hwSetName,             # display name, first spelling used
    'capacity': int,                    # units currently in the pool
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
Checkout, and Checkin actions. A set is a flat count of units: there is no
per-location split and no per-checkin history -- those belonged to a prior
domain-specific
extension that has been removed.

`availability` (capacity - reservedQuantity, floored at 0) is derived on
read and never stored.

This module holds ONLY the hardware-set store. Project membership lives in
the separate `Projects` collection (Track A owns writes to it); this module
reads nothing from it directly -- that is projectsDatabase's job via
assertProjectMember.
'''

HARDWARE_SETS_COLLECTION = "HardwareSets"
PROJECTS_COLLECTION = "Projects"

_WHITESPACE_RUN = re.compile(r"\s+")


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


class ConcurrentModificationError(Exception):
    """Raised when checkoutHardware loses the optimistic-concurrency race
    three times in a row -- another writer kept winning the conditional
    update. Maps to HTTP 409.
    """


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
    normalization -- no substring or fuzzy matching, which an earlier
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


def checkinHardware(client, projectId, rawName, quantity):
    """Check in `quantity` units of a hardware set, creating it if it does
    not already exist for this project. Increments the stored `capacity`
    by `quantity` in the same update as the upsert.

    Resolution: an exact (normalized) name match merges into the existing
    hardware set and its stored hwSetName is left untouched, so the
    project keeps the display name it first chose. No match creates a new
    hardware set; hwSetKey is the normalized name and hwSetName is the raw
    name as typed.
    """
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
        raise InvalidInventoryInput("quantity")

    try:
        normalizedName = normalizeHwSetName(rawName)
    except ValueError:
        raise InvalidInventoryInput("hwSetName")

    db = client[DB_NAME]
    collection = db[HARDWARE_SETS_COLLECTION]
    _ensureHwSetUniqueIndex(collection)

    upsertFilter = {"projectId": projectId, "hwSetKey": normalizedName}
    upsertUpdate = {
        "$inc": {"capacity": quantity},
        "$setOnInsert": {
            "projectId": projectId,
            "hwSetKey": normalizedName,
            "hwSetName": rawName,
            "reservations": [],
            "reservedQuantity": 0,
        },
    }

    try:
        updated = collection.find_one_and_update(
            upsertFilter, upsertUpdate, upsert=True, return_document=ReturnDocument.AFTER
        )
    except DuplicateKeyError:
        # Another concurrent check-in of the same brand-new hardware-set
        # name won the race and inserted first; the unique index caught
        # our upsert attempting a duplicate insert. The document now
        # exists, so the identical filter/update retried here matches it
        # and becomes a plain read-merge-write ($inc), no insert attempted
        # this time.
        updated = collection.find_one_and_update(
            upsertFilter, upsertUpdate, upsert=True, return_document=ReturnDocument.AFTER
        )

    return _serializeHardwareSet(updated)


_MAX_CONCURRENCY_ATTEMPTS = 3


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


def checkoutHardware(client, projectId, rawName, quantity):
    """Check out `quantity` units of a hardware set, decrementing its
    `capacity`.

    Raises InsufficientStockError (carrying onHand/requested) when
    quantity exceeds the hardware set's `capacity` -- read, not
    `availability`, matching the prior inventory model's overbooking rule:
    checkout draws from total stock regardless of outstanding requests. A
    rejected or lost checkout never writes anything; the write itself is a
    single find_one_and_update pinned to the exact `capacity` that was
    read (reservedQuantity is deliberately NOT pinned -- checkout never
    reads or writes it, so pinning on it would spuriously fail this
    conditional update on any unrelated concurrent request/release),
    retried up to _MAX_CONCURRENCY_ATTEMPTS times on a lost race before
    raising ConcurrentModificationError.
    """
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
        raise InvalidInventoryInput("quantity")

    db = client[DB_NAME]
    collection = db[HARDWARE_SETS_COLLECTION]

    targetKey = _resolveExistingHwSetKey(collection, projectId, rawName)

    for _attempt in range(_MAX_CONCURRENCY_ATTEMPTS):
        doc = collection.find_one({"projectId": projectId, "hwSetKey": targetKey})
        if doc is None:
            raise ItemNotFoundError(rawName)

        capacity = doc.get("capacity", 0)

        if quantity > capacity:
            raise InsufficientStockError(onHand=capacity, requested=quantity)

        updated = collection.find_one_and_update(
            {
                "_id": doc["_id"],
                "capacity": capacity,
            },
            {
                "$set": {"capacity": capacity - quantity},
            },
            return_document=ReturnDocument.AFTER,
        )

        if updated is not None:
            return _serializeHardwareSet(updated)

    raise ConcurrentModificationError(
        "lost the checkout race after {} attempts".format(_MAX_CONCURRENCY_ATTEMPTS)
    )


def addReservation(client, projectId, rawName, quantity, userId, userName):
    """Append a reservation entry (a "Request", per SN3) to the hardware set
    and increment reservedQuantity.

    Never compares quantity against capacity -- requesting beyond what is
    on hand is a legitimate thing for a project member to do; the
    overbooking guard applies to checkout only. Uses a single $push/$inc
    update so two simultaneous requests both survive rather than one
    overwriting the other.
    """
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
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
        {"projectId": projectId, "hwSetKey": targetKey},
        {
            "$push": {"reservations": reservation},
            "$inc": {"reservedQuantity": quantity},
        },
        return_document=ReturnDocument.AFTER,
    )

    if updated is None:
        raise ItemNotFoundError(rawName)

    return reservationId, _serializeHardwareSet(updated)


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

    return _serializeHardwareSet(updated)


def getHardwareStatus(client, projectId):
    """Return a list of hardware-set dicts for the project, sorted by
    display name for deterministic, repeatable ordering.
    """
    db = client[DB_NAME]
    collection = db[HARDWARE_SETS_COLLECTION]

    items = [_serializeHardwareSet(doc) for doc in collection.find({"projectId": projectId})]
    items.sort(key=lambda item: item.get("hwSetKey", ""))
    return items


def _serializeHardwareSet(doc):
    """Convert a raw Mongo document into a JSON-serializable hardware-set
    dict with `available` derived.

    The API boundary uses "request"/"requestId"/"requestedQuantity"/
    "available" (the assignment mockup's own Figure 3 vocabulary) even
    though the internal storage/implementation below this line keeps its
    original "reservation"/"availability" naming -- only this serializer
    and the /api/hardware/request+release routes in app.py know about the
    translation, so client and server agree on the wire format without a
    repo-wide rename of the underlying reservation machinery.
    """
    capacity = doc.get("capacity", 0)
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

    return {
        "_id": str(doc["_id"]) if isinstance(doc.get("_id"), ObjectId) else doc.get("_id"),
        "projectId": doc.get("projectId"),
        "hwSetKey": doc.get("hwSetKey"),
        "hwSetName": doc.get("hwSetName"),
        "capacity": capacity,
        "requests": requests,
        "requestedQuantity": reservedQuantity,
        "available": max(capacity - reservedQuantity, 0),
    }
