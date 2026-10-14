# Import necessary libraries and modules
from pymongo import MongoClient

import hardwareDatabase as hardwareDB

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
    db = client["HardwareCheckout"]
    projects = db["Projects"]

    # matching ID 
    project = projects.find_one({"projectID" : projectId})

    return project 


# Function to create a new project
def createProject(client, projectName, projectId, description):
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
        "users": []
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

