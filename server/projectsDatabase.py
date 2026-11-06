"""Data-access helpers for project data.

Like hardwareDatabase, these functions operate on a small collection interface
shared by PyMongo and the in-memory development collection, so the API does not
change when the team connects MongoDB.

Structure of a stored project document:
Project = {
    'projectName': projectName,
    'projectId': projectId,
    'description': description,
    'hwSets': {HW1: 0, HW2: 10, ...},
    'users': [user1, user2, ...]
}
"""

import re

from pymongo.errors import DuplicateKeyError


PROJECT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 1000


class ProjectExistsError(Exception):
    """Raised when a project with the requested projectId already exists."""



class ProjectNotFoundError(Exception):
    """Raised when an operation targets a projectId that does not exist."""


class AlreadyMemberError(Exception):
    """Raised when a user tries to join a project they already belong to."""

def serializeProject(document):
    """Convert a stored project document into the public API shape."""
    if document is None:
        return None

    return {
        "projectName": document.get("projectName", ""),
        "projectId": document.get("projectId", ""),
        "description": document.get("description", ""),
        "hwSets": dict(document.get("hwSets", {})),
        "users": list(document.get("users", [])),
    }


def _validateProjectFields(projectName, projectId, description):
    """Return cleaned fields or raise ValueError with a user-facing message."""
    if not isinstance(projectName, str) or not projectName.strip():
        raise ValueError("Project name is required.")
    projectName = projectName.strip()
    if len(projectName) > MAX_NAME_LENGTH:
        raise ValueError(
            f"Project name must be {MAX_NAME_LENGTH} characters or fewer."
        )

    if not isinstance(projectId, str) or not projectId.strip():
        raise ValueError("Project ID is required.")
    projectId = projectId.strip()
    if not PROJECT_ID_PATTERN.match(projectId):
        raise ValueError(
            "Project ID must be 1-32 characters using letters, numbers, "
            "hyphens, or underscores."
        )

    if description is None:
        description = ""
    if not isinstance(description, str):
        raise ValueError("Description must be text.")
    description = description.strip()
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise ValueError(
            f"Description must be {MAX_DESCRIPTION_LENGTH} characters or fewer."
        )

    return projectName, projectId, description


def queryProject(collection, projectId):
    """Return one project by its ID, or None if it does not exist."""
    return serializeProject(collection.find_one({"projectId": projectId}))


def createProject(collection, projectName, projectId, description="", creatorId=None):
    """Create a new project and return its normalized representation.

    The creator, when known, becomes the project's first member. Raises
    ValueError for invalid input and ProjectExistsError for a taken projectId.
    """
    projectName, projectId, description = _validateProjectFields(
        projectName, projectId, description
    )

    if collection.find_one({"projectId": projectId}) is not None:
        raise ProjectExistsError(f"Project ID '{projectId}' is already taken.")

    document = {
        "projectName": projectName,
        "projectId": projectId,
        "description": description,
        "hwSets": {},
        "users": [creatorId] if creatorId else [],
    }
    try:
        collection.insert_one(document)
    except DuplicateKeyError as error:
        # Covers the race where two requests claim the same ID at once
        # (requires the unique index on projectId created in app.py).
        raise ProjectExistsError(
            f"Project ID '{projectId}' is already taken."
        ) from error
    return serializeProject(document)


def listUserProjects(collection, userId):
    """Return every project the user belongs to (issue #6: View My Projects).

    In MongoDB, {"users": userId} matches any project whose users list
    contains userId. Projects come back sorted by name so the dashboard
    order is stable. Raises ValueError if userId is missing.
    """
    if not isinstance(userId, str) or not userId.strip():
        raise ValueError("User ID is required.")
    userId = userId.strip()

    projects = [
        serializeProject(document)
        for document in collection.find({"users": userId})
    ]
    return sorted(projects, key=lambda project: project["projectName"].lower())


def listProjects(collection):
    """Return every project sorted by name."""
    projects = [serializeProject(document) for document in collection.find({})]
    return sorted(projects, key=lambda project: project["projectName"].lower())

# --- Not yet implemented (see issues #5 and #18-#24) -----------------------

def addUser(collection, projectId, userId):
    """Add a user to the specified project (issue #5: Join a Project).

    The update only matches when the user is not already listed, so two
    simultaneous joins can never add the same user twice. Returns the updated
    project. Raises ValueError for missing input, ProjectNotFoundError for an
    unknown projectId, and AlreadyMemberError if the user already belongs.
    """
    if not isinstance(userId, str) or not userId.strip():
        raise ValueError("User ID is required.")
    userId = userId.strip()

    if not isinstance(projectId, str) or not projectId.strip():
        raise ValueError("Project ID is required.")
    projectId = projectId.strip()

    result = collection.update_one(
        {"projectId": projectId, "users": {"$ne": userId}},
        {"$addToSet": {"users": userId}},
    )

    if result.matched_count == 0:
        # Nothing matched: either the project is missing or the user is
        # already a member. Look it up to tell the two apart.
        if collection.find_one({"projectId": projectId}) is None:
            raise ProjectNotFoundError(f"Project '{projectId}' was not found.")
        raise AlreadyMemberError(
            f"You are already a member of project '{projectId}'."
        )

    return queryProject(collection, projectId)


# --- Not yet implemented (see issues #18-#24) ------------------------------


def updateUsage(collection, projectId, hwSetName):
    """Update the usage of a hardware set in the specified project."""
    raise NotImplementedError


def checkOutHW(collection, projectId, hwSetName, qty, userId):
    """Check out hardware for the specified project and update availability."""
    raise NotImplementedError


def checkInHW(collection, projectId, hwSetName, qty, userId):
    """Check in hardware for the specified project and update availability."""
    raise NotImplementedError
