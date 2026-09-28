# Import necessary libraries and modules
import projectsDatabase as projectsDB
from config import DB_NAME
from passwordSecurity import InvalidPasswordError, hashPassword, verifyPassword

'''
Structure of User entry:
User = {
    'username': username,
    'userId': userId,
    'password': password,   # bcrypt hash -- plaintext is never stored (SR3)
    'projects': [project1_ID, project2_ID, ...]
}
'''

USERS_COLLECTION = "Users"


class UserAlreadyExistsError(Exception):
    """Raised by addUser when userId is already taken."""


# Function to add a new user
def addUser(client, username, userId, password):
    """Create a new user, storing a bcrypt hash of password, never the
    plaintext itself.

    Raises InvalidPasswordError (from passwordSecurity) if password fails
    validation, or UserAlreadyExistsError if userId is already taken.
    """
    hashedPassword = hashPassword(password)  # raises InvalidPasswordError

    collection = client[DB_NAME][USERS_COLLECTION]

    if collection.find_one({"userId": userId}) is not None:
        raise UserAlreadyExistsError(userId)

    collection.insert_one({
        "username": username,
        "userId": userId,
        "password": hashedPassword,
        "projects": [],
    })


# Helper function to query a user by username and userId
def __queryUser(client, username, userId):
    # Query and return a user from the database
    collection = client[DB_NAME][USERS_COLLECTION]
    return collection.find_one({"username": username, "userId": userId})


# A hash of a value nobody will ever actually submit as a password, used
# only to give the "no such user" path in login() a bcrypt comparison to
# run -- so it costs roughly the same time as a real wrong-password check
# and a failed login can't be used to enumerate valid userIds by timing.
_DUMMY_HASH = hashPassword("no-such-user-placeholder")


# Function to log in a user
def login(client, username, userId, password):
    """Authenticate a user against their stored bcrypt hash.

    Returns True on success, False for any mismatch -- unknown
    username/userId and wrong password are indistinguishable to the
    caller, on purpose.
    """
    user = __queryUser(client, username, userId)
    if user is None:
        verifyPassword(password, _DUMMY_HASH)
        return False

    return verifyPassword(password, user["password"])


# Function to add a user to a project
def joinProject(client, userId, projectId):
    # Add a user to a specified project
    pass

# Function to get the list of projects for a user
def getUserProjectsList(client, userId):
    # Get and return the list of projects a user is part of
    pass
