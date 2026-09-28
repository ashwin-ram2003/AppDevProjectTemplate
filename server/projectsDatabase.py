# Import necessary libraries and modules
from pymongo import MongoClient

import hardwareDatabase as hardwareDB

'''
Structure of Project entry:
Project = {
    'projectName': projectName,
    'projectId': projectId,
    'description': description,
    'users': [user1, user2, ...]
}

Hardware-set stock (Track B) is superseded by hardwareDatabase's own
docstring: it now lives in the separate `HardwareSets` collection
(projectId + hwSetKey), not nested in this document. This document's
`users` list remains the source of truth for project membership; see
assertProjectMember below.
'''

# Function to query a project by its ID
def queryProject(client, projectId):
    # Query and return a project from the database
    pass

# Function to create a new project
def createProject(client, projectName, projectId, description):
    # Create a new project in the database
    pass

# Function to add a user to a project
def addUser(client, projectId, userId):
    # Add a user to the specified project
    pass

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
# the `Projects` collection only to check membership (`users` list); it
# never reads or writes project document fields Track A owns (projectName,
# description, etc. above).
#
# The project document is identified by its `projectId` field. Track A's
# createProject must write that field name when it lands, or this guard
# will not find the document it just created.
# ---------------------------------------------------------------------------


class NotAProjectMemberError(Exception):
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
    """Trust-boundary guard: raise NotAProjectMemberError unless userId is
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
        raise NotAProjectMemberError(userId)

    db = client[hardwareDB.DB_NAME]
    project = db[hardwareDB.PROJECTS_COLLECTION].find_one({"projectId": projectId})

    if project is None or userId not in project.get("users", []):
        raise NotAProjectMemberError(userId)



def checkinHardwareSet(client, projectId, userId, hwSetName, quantity):
    """Check in units of a hardware set after verifying project membership."""
    assertProjectMember(client, projectId, userId)
    return hardwareDB.checkinHardware(client, projectId, hwSetName, quantity)


def getProjectHardwareStatus(client, projectId, userId):
    """Return the project's hardware-set status list after verifying
    project membership.
    """
    assertProjectMember(client, projectId, userId)
    return hardwareDB.getHardwareStatus(client, projectId)


def checkoutHardwareSet(client, projectId, userId, hwSetName, quantity):
    """Check out units of a hardware set after verifying project
    membership. Requests (reservations) never gate this call -- the guard
    hardwareDB.checkoutHardware applies compares the requested quantity
    against capacity alone.
    """
    assertProjectMember(client, projectId, userId)
    return hardwareDB.checkoutHardware(client, projectId, hwSetName, quantity)


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

