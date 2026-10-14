# Import necessary libraries and modules
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

import projectsDatabase as projectsDB

'''
Structure of User entry:
User = {
    'username': username,
    'userId': hashed userId (see encryption.py),
    'password': hashed password (werkzeug),
    'projects': [project1_ID, project2_ID, ...]
}
'''

# Function to add a new user
def addUser(client, username, userId, password):
    # Add a new user to the database
    users = client['HardwareCheckout']['Users']
    
    # Prevent duplicate user IDs
    if users.find_one({'userId': userId}) is not None:
        return False

    user = {'username': username,
            'userId': userId,
            'password': generate_password_hash(password),
            'projects': []}

    users.insert_one(user)
    return True

# Helper function to query a user by username and userId
def __queryUser(client, username, userId):
    # Query and return a user from the database
    users = client['HardwareCheckout']['Users']

    return users.find_one({'username': username,
                           'userId': userId})

# Function to log in a user
def login(client, username, userId, password):
    # Authenticate a user and return login status
    user = __queryUser(client, username, userId)

    if user is None:
        return False

    # Compare against the stored hash
    return check_password_hash(user['password'], password)

# Function to add a user to a project
def joinProject(client, userId, projectId):
    # Add a user to a specified project
    users = client['HardwareCheckout']['Users']

    user = users.find_one({'userId': userId})
    if user is None:
        return False

    # Verify that the project exists
    project = projectsDB.queryProject(client, projectId)
    if project is None:
        return False

    # Avoid adding the same project twice
    if projectId in user['projects']:
        return False

    # Add the project to the user
    users.update_one({'userId': userId},
                     {'$addToSet': {'projects': projectId}})

    # Add the user to the project's membership list
    if not projectsDB.addUser(client, projectId, userId):
        # Roll back the user's project member if update fails
        users.update_one({'userId': userId},
                         {'$pull': {'projects': projectId}})
        return False
    return True

# Function to get the list of projects for a user
def getUserProjectsList(client, userId):
    # Get and return the list of projects a user is part of
    users = client['HardwareCheckout']['Users']
    user = users.find_one({'userId': userId})

    if user is None:
        return None
    return user['projects']

