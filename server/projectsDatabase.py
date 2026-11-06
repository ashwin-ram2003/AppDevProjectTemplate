# Import necessary libraries and modules
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import hardwareDatabase as hardwareDB

'''
Structure of Project entry:
Project = {
    'projectName': projectName,
    'projectId': projectId,
    'description': description,
    'hwSets': {HW1: 0, HW2: 10, ...},
    'users': [user1, user2, ...],
    'owner': hashed userId of the creator
}
'''
# Database and collection names
DB_NAME = 'HardwareCheckout'
COLLECTION = 'Projects'

# Helper function: gets the projects collection from client
def getCollection(client):
    return client[DB_NAME][COLLECTION]

# Helper function: check if number is an int
def isInt(value):
    return isinstance(value, int) and not isinstance(value, bool)

# Helper function: give units back to a hardware set using updateAvailability
# (it rejects anything that would push availability above capacity)
def returnUnits(client, hwSetName, qty):
    hw_set = hardwareDB.queryHardwareSet(client, hwSetName)
    if hw_set is None:
        return False
    return hardwareDB.updateAvailability(client, hwSetName, hw_set['availability'] + qty)

# Function to query a project by its ID
def queryProject(client, projectId):
    # Query and return a project from the database
    db = client["HardwareCheckout"]
    projects = db["Projects"]

    # matching ID
    project = projects.find_one({"projectId" : projectId})

    return project

# Function to query several projects at once, in the order of projectIds
def queryProjects(client, projectIds):
    found = {p['projectId']: p for p in getCollection(client).find({'projectId': {'$in': projectIds}})}
    return [found[pid] for pid in projectIds if pid in found]

# Helper function: the project's owner. Projects made before owners were stored
# fall back to their first member, which is the creator
def getOwner(project):
    return project.get('owner') or next(iter(project.get('users') or []), None)

def hasMember(client, projectId, userId):
    project = queryProject(client, projectId)
    return project is not None and userId in project.get('users', [])

# Function to create a new project
def createProject(client, projectName, projectId, description, owner=None):
    # Create a new project in the database
    db = client["HardwareCheckout"]
    projects = db["Projects"]

    # check if exists
    if queryProject(client, projectId) is not None:
        return False

    # create a new project
    project = {
        "projectName": projectName,
        "projectId": projectId,
        "description": description,
        "hwSets": {},
        "users": [],
        "owner": owner
    }

    # insert project
    projects.insert_one(project)

    return True

# Function to add a user to a project
def addUser(client, projectId, userId):
    # add user
    db = client["HardwareCheckout"]
    projects = db["Projects"]

    # find project
    project = queryProject(client, projectId)

    if project is None:
        return False

    # is user alr in project
    if userId in project["users"]:
        return False

    # add project to list
    projects.update_one(
        {"projectId": projectId},
        {"$push": {"users": userId}}
    )

    return True

# Function to update hardware usage in a project
def updateUsage(client, projectId, hwSetName, delta):
    # Update the usage of a hardware set in the specified project
    # delta > 0 adds to the project's usage, delta < 0 removes from it
    if not hwSetName or not isInt(delta) or delta == 0:
        return False

    query = {'projectId': projectId}
    if delta < 0:
        # Usage may never drop below zero (can't check in more than was checked out)
        query[f'hwSets.{hwSetName}'] = {'$gte': -delta}

    result = getCollection(client).update_one(
        query,
        {'$inc': {f'hwSets.{hwSetName}': delta}}
    )
    return result.matched_count == 1

# Function to check out hardware for a project
def checkOutHW(client, projectId, hwSetName, qty, userId):
    # Check out hardware for the specified project and update availability
    if not isInt(qty) or qty <= 0 or not userId or not hasMember(client, projectId, userId):
        return False
    if not hasMember(client, projectId, userId):
        return False

    # Take the units from the hardware set (atomic, fails if not enough available)
    if not hardwareDB.requestSpace(client, hwSetName, qty):
        return False

    # Record the units against the project; hand them back if that fails
    if not updateUsage(client, projectId, hwSetName, qty):
        returnUnits(client, hwSetName, qty)
        return False
    return True

# Function to check in hardware for a project
def checkInHW(client, projectId, hwSetName, qty, userId):
    # Check in hardware for the specified project and update availability
    if not isInt(qty) or qty <= 0 or not userId or not hasMember(client, projectId, userId):
        return False

    # Remove the units from the project first (fails if it has fewer checked out)
    if not updateUsage(client, projectId, hwSetName, -qty):
        return False

    # Return the units to the hardware set; undo the project change if that fails
    if not returnUnits(client, hwSetName, qty):
        updateUsage(client, projectId, hwSetName, qty)
        return False
    return True
