# Import necessary libraries and modules
import hardwareDatabase as hardwareDB
import projectsDatabase as projectsDB
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

# Reuse hardwareDatabase's DB_NAME (same convention as projectsDatabase.py)
# rather than defining a second MONGODB_DB default here -- users, projects,
# and hardware sets must all land in the same database.
DB_NAME = hardwareDB.DB_NAME
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
    """Add userId to the given project's membership list (US-04).

    Delegates to projectsDatabase.addUser for the actual write; see there
    for the idempotency note and ProjectNotFoundError.
    """
    projectsDB.addUser(client, projectId, userId)

# Function to get the list of projects for a user
def getUserProjectsList(client, userId):
    """Return every project userId belongs to (US-05).

    Delegates to projectsDatabase -- a project's own `users` list is the
    source of truth for membership, not a field on the user document
    (see projectsDatabase.py's module docstring and addUser above).
    """
    return projectsDB.getUserProjects(client, userId)
