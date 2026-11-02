# Import necessary libraries and modules
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import hardwareDatabase as hardwareDB

'''
Structure of Project entry (collection `Households` -- see
hardwareDB.PROJECTS_COLLECTION; name kept from an earlier domain
iteration, every field below is project vocabulary):

Project = {
    'householdId': projectId,   # stored field name; wire name is projectId
    'projectName': projectName,
    'description': description,
    'users': [user1, user2, ...]
}

Hardware-set stock (Track B) is superseded by hardwareDatabase's own
docstring: it now lives in the separate `HardwareSets` collection
(projectId + hwSetKey), not nested in this document. This document's
`users` list remains the source of truth for project membership; see
assertProjectMember below.
'''


class ProjectNotFoundError(Exception):
    """Raised when projectId does not match any existing project. Maps to
    HTTP 404.
    """


class ProjectAlreadyExistsError(Exception):
    """Raised by createProject when projectId is already taken. Maps to
    HTTP 409.
    """


class InvalidProjectInput(Exception):
    """Raised when a project field is missing or the wrong type. Maps to
    HTTP 400; the message carries the offending field name.

    Type-checking (not just presence) matters here for the same reason it
    does in assertProjectMember below: request.get_json() decodes
    arbitrary JSON, and an unvalidated dict value passed into a Mongo
    filter could be interpreted as a query operator instead of a literal
    match.
    """


def _serializeProject(doc):
    """Strip Mongo's _id and rename the stored householdId field to the
    wire name projectId.
    """
    return {
        "projectId": doc["householdId"],
        "projectName": doc.get("projectName", ""),
        "description": doc.get("description", ""),
        "users": doc.get("users", []),
    }


def _ensureProjectUniqueIndex(collection):
    """Create the unique index backing createProject's insert.

    Without this, two concurrent createProject calls for the same
    projectId could both pass the "does it already exist" read and both
    insert -- the same race createHardwareSet's own unique index guards
    against (see hardwareDatabase.py's _ensureHwSetUniqueIndex).
    create_index is idempotent, so calling it on every createProject is
    safe and needs no separate migration step.
    """
    collection.create_index("householdId", unique=True, name="uniq_householdId")


# Function to query a project by its ID
def queryProject(client, projectId):
    """Return the project identified by projectId as a serialized dict, or
    None if no such project exists.

    Raises InvalidProjectInput if projectId is not a non-empty string.
    """
    if not isinstance(projectId, str) or not projectId:
        raise InvalidProjectInput("projectId")

    db = client[hardwareDB.DB_NAME]
    doc = db[hardwareDB.PROJECTS_COLLECTION].find_one({"householdId": projectId})
    return _serializeProject(doc) if doc is not None else None


# Function to create a new project
def createProject(client, projectName, projectId, description, creatorUserId):
    """Create a new project (US-03), with creatorUserId as its first
    member so its creator can use it immediately without a separate join.

    Raises InvalidProjectInput if any field is missing or the wrong type,
    or ProjectAlreadyExistsError if projectId is already taken.
    """
    fields = {
        "projectName": projectName,
        "projectId": projectId,
        "description": description,
        "creatorUserId": creatorUserId,
    }
    for field, value in fields.items():
        if not isinstance(value, str) or not value:
            raise InvalidProjectInput(field)

    db = client[hardwareDB.DB_NAME]
    collection = db[hardwareDB.PROJECTS_COLLECTION]
    _ensureProjectUniqueIndex(collection)

    doc = {
        "householdId": projectId,
        "projectName": projectName,
        "description": description,
        "users": [creatorUserId],
    }
    try:
        collection.insert_one(doc)
    except DuplicateKeyError:
        raise ProjectAlreadyExistsError(projectId)

    return _serializeProject(doc)


# Function to return every project a user belongs to
def getUserProjects(client, userId):
    """Return every project userId belongs to (US-05), as serialized
    dicts ordered by projectId for a stable list across repeated calls.

    Raises InvalidProjectInput if userId is not a non-empty string.
    """
    if not isinstance(userId, str) or not userId:
        raise InvalidProjectInput("userId")

    db = client[hardwareDB.DB_NAME]
    docs = db[hardwareDB.PROJECTS_COLLECTION].find({"users": userId})
    return sorted(
        (_serializeProject(doc) for doc in docs),
        key=lambda project: project["projectId"],
    )


# Function to add a user to a project
def addUser(client, projectId, userId):
    """Add userId to the project's membership list (US-04).

    Idempotent -- joining a project you're already in is a no-op, not an
    error, so this is safe to call on every sign-in as a self-healing
    step, not just once at sign-up.

    Raises ProjectNotFoundError if projectId does not match any existing
    project.

    projectId and userId must be plain strings, for the same injection
    reason assertProjectMember below validates them -- request.get_json()
    decodes arbitrary JSON, and an unvalidated dict value here could be
    interpreted by Mongo as a query operator instead of a literal match.
    """
    if not isinstance(projectId, str) or not isinstance(userId, str):
        raise ProjectNotFoundError(projectId)

    db = client[hardwareDB.DB_NAME]
    result = db[hardwareDB.PROJECTS_COLLECTION].update_one(
        {"householdId": projectId},
        {"$addToSet": {"users": userId}},
    )
    if result.matched_count == 0:
        raise ProjectNotFoundError(projectId)

# Function to update hardware usage in a project
def updateUsage(client, projectId, hwSetName):
    # Update the usage of a hardware set in the specified project
    pass

# Function to check out hardware for a project
def checkOutHW(client, projectId, hwSetName, qty, userId):
    # Check out hardware for the specified project and update availability
    pass

# Function to check in hardware for a project
def checkInHW(client, projectId, hwSetName, qty, userId):
    # Check in hardware for the specified project and update availability
    pass


# ---------------------------------------------------------------------------
# Track B — hardware resource management (generic HaaS domain)
#
# Hardware-set stock lives in the separate `HardwareSets` collection
# (hardwareDatabase.py), keyed by projectId + hwSetKey. This section reads
# the `Households` collection only to check membership (`users` list); it
# never reads or writes project document fields Track A owns (projectName,
# etc. above). (The collection is still named `Households` on disk from an
# earlier domain iteration -- see hardwareDB.PROJECTS_COLLECTION -- but every
# field and function here is project/hardware vocabulary, not food/household.)
# ---------------------------------------------------------------------------


class NotAHouseholdMemberError(Exception):
    """Raised when userId is not a member of the project. Maps to HTTP 403.
    (Class name kept for backward compatibility with existing callers/tests;
    semantically this is "not a project member".)
    """


# Re-exported so the route layer can catch it as projectsDB.ReservationNotOwnedError
# alongside the other Track B exceptions, without reaching into hardwareDatabase
# directly for it. The class itself is defined in hardwareDatabase.py because
# hardwareDatabase.removeReservation is what detects the ownership mismatch.
ReservationNotOwnedError = hardwareDB.ReservationNotOwnedError


def assertProjectMember(client, projectId, userId):
    """Trust-boundary guard: raise NotAHouseholdMemberError unless userId is
    a member of the project identified by projectId. Every hardware route
    calls this first, before touching any stock.

    projectId and userId must be plain strings. request.get_json() decodes
    arbitrary JSON, so without this check a client could pass a dict (e.g.
    {"$ne": "..."}) that Mongo would interpret as a query operator instead
    of an equality match, defeating project isolation for this function and
    every hardwareDatabase filter built from the same unvalidated value
    downstream.
    """
    if not isinstance(projectId, str) or not isinstance(userId, str):
        raise NotAHouseholdMemberError(userId)

    db = client[hardwareDB.DB_NAME]
    project = db[hardwareDB.PROJECTS_COLLECTION].find_one({"householdId": projectId})

    if project is None or userId not in project.get("users", []):
        raise NotAHouseholdMemberError(userId)


# Backward-compatible alias -- older call sites/tests may still import this name.
assertHouseholdMember = assertProjectMember


def createHardwareSet(client, projectId, userId, hwSetName, capacity):
    """Create a hardware set with a fixed starting capacity after verifying
    project membership. Idempotent if the set already exists -- see
    hardwareDB.createHardwareSet's docstring; capacity is never overwritten
    by a repeat call.
    """
    assertProjectMember(client, projectId, userId)
    return hardwareDB.createHardwareSet(client, projectId, hwSetName, capacity)


def checkinHardwareSet(client, projectId, userId, hwSetName, quantity):
    """Check in units of a hardware set after verifying project membership.

    Gated by what userId personally checked out (hardwareDB.checkinHardware),
    not the project-wide total -- see hardwareDatabase.py's module docstring.
    """
    assertProjectMember(client, projectId, userId)
    return hardwareDB.checkinHardware(client, projectId, hwSetName, quantity, userId)


def getProjectHardwareStatus(client, projectId, userId):
    """Return the project's hardware-set status list after verifying
    project membership. Each item's `myCheckedOut` reflects userId's own
    holdings specifically, not the project-wide total.
    """
    assertProjectMember(client, projectId, userId)
    return hardwareDB.getHardwareStatus(client, projectId, userId)


def checkoutHardwareSet(client, projectId, userId, hwSetName, quantity):
    """Check out units of a hardware set after verifying project
    membership. Requests (reservations) never gate this call -- the guard
    hardwareDB.checkoutHardware applies compares the requested quantity
    against capacity alone. Credits the checked-out units to userId's own
    `checkedOutBy` entry.
    """
    assertProjectMember(client, projectId, userId)
    return hardwareDB.checkoutHardware(client, projectId, hwSetName, quantity, userId)


def requestHardwareSet(client, projectId, userId, userName, hwSetName, quantity):
    """Claim (request) a quantity of a hardware set under userId/userName
    after verifying project membership. Never compares quantity against
    what is on hand -- the overbooking guard applies to checkout only.
    """
    assertProjectMember(client, projectId, userId)
    return hardwareDB.addReservation(
        client, projectId, hwSetName, quantity, userId, userName
    )


def releaseReservation(client, projectId, userId, reservationId):
    """Release a reservation after verifying project membership. Only the
    member who created the reservation can release it --
    hardwareDB.removeReservation enforces that and raises
    ReservationNotOwnedError otherwise.
    """
    assertProjectMember(client, projectId, userId)
    return hardwareDB.removeReservation(client, projectId, reservationId, userId)

