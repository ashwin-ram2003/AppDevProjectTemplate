# Import necessary libraries and modules
#from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

#import projectsDatabase as projectsDB

'''
Structure of User entry:
User = {
    'username': username,
    'userId': userId,
    'password': password,
    'projects': [project1_ID, project2_ID, ...]
}
'''

# Function to add a new user



def addUser(collection, username, userId, password):
    """Create a user unless the userId already exists."""

    existing_user = collection.find_one({"userId": userId})

    if existing_user is not None:
        return None

    user = {
        "username": username,
        "userId": userId,
        "password": generate_password_hash(password),
        "projects": [],
    }

    collection.insert_one(user)

    return {
        "username": username,
        "userId": userId,
        "projects": [],
    }
# Helper function to query a user by username and userId
def __queryUser(client, username, userId):
    # Query and return a user from the database
    pass

# Function to log in a user
def login(collection, userId, password):
    """Authenticate a user by user ID and password."""

    user = collection.find_one({"userId": userId})

    if user is None:
        return None

    if not check_password_hash(user["password"], password):
        return None

    return {
        "username": user.get("username", userId),
        "userId": user["userId"],
        "projects": user.get("projects", []),
    }

# Function to add a user to a project
def joinProject(client, userId, projectId):
    # Add a user to a specified project
    pass

# Function to get the list of projects for a user
def getUserProjectsList(client, userId):
    # Get and return the list of projects a user is part of
    pass

