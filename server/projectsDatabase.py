# Import necessary libraries and modules
from pymongo import MongoClient

import hardwareDB

'''
Structure of Project entry:
Project = {
    'projectName': projectName,
    'projectId': projectId,
    'description': description,
    'hwSets': {HW1: 0, HW2: 10, ...},
    'users': [user1, user2, ...]
}
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

# Get the hardware usage for a project
def updateUsage(client, projectId, hwSetName):
    # Find the project
    project = queryProject(client, projectId)
 
    # Check if the project exists
    if project is None:
        return None
 
    # Get the hardware sets used by the project
    hwSets = project["hwSets"]
 
    # Return the quantity currently being used
    return hwSets.get(hwSetName, 0)
 
 
# Check out hardware for a project
def checkOutHW(client, projectId, hwSetName, qty, userId):
    db = client["HardwareCheckout"]
    projects = db["Projects"]
 
    # Find the project
    project = queryProject(client, projectId)
 
    # Check if the project exists
    if project is None:
        return False
 
    # Check if the user belongs to the project
    if userId not in project["users"]:
        return False
 
    # Make sure the quantity is positive
    if type(qty) is not int or qty <= 0:
        return False
 
    # Find the hardware set
    hardware = hardwareDB.queryHardwareSet(client, hwSetName)
 
    # Check if the hardware exists
    if hardware is None:
        return False
 
    # Check if enough hardware is available
    if hardware["availability"] < qty:
        return False
 
    # Request the hardware from inventory
    hardwareDB.requestSpace(client, hwSetName, qty)
 
    # Increase the project's hardware usage
    projects.update_one(
        {"projectId": projectId},
        {"$inc": {"hwSets." + hwSetName: qty}}
    )
 
    return True
 
 
# Check in hardware for a project
def checkInHW(client, projectId, hwSetName, qty, userId):
    db = client["HardwareCheckout"]
    projects = db["Projects"]
 
    # Find the project
    project = queryProject(client, projectId)
 
    # Check if the project exists
    if project is None:
        return False
 
    # Check if the user belongs to the project
    if userId not in project["users"]:
        return False
 
    # Make sure the quantity is positive
    if type(qty) is not int or qty <= 0:
        return False
 
    # Get the quantity currently checked out
    currentUsage = updateUsage(client, projectId, hwSetName)
 
    # Make sure the project has enough to return
    if qty > currentUsage:
        return False
 
    # Find the hardware set
    hardware = hardwareDB.queryHardwareSet(client, hwSetName)
 
    # Check if the hardware exists
    if hardware is None:
        return False
 
    # Calculate the new availability
    newAvailability = hardware["availability"] + qty
 
    # Update the available hardware
    hardwareDB.updateAvailability(client, hwSetName, newAvailability)
 
    # Decrease the project's hardware usage
    projects.update_one(
        {"projectId": projectId},
        {"$inc": {"hwSets." + hwSetName: -qty}}
    )
 
    return True
 