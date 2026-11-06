"""Flask application for user, project, and hardware APIs."""

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError



try:
    from .dummyHardwareData import DUMMY_HARDWARE, InMemoryHardwareCollection
    from .dummyProjectData import DUMMY_PROJECTS, InMemoryProjectCollection
    from .hardwareDatabase import (
        HardwareExistsError,
        createHardwareSet,
        listHardwareSets,
        queryHardwareSet,
        requestSpace,
    )
    from .projectsDatabase import (
        AlreadyMemberError,
        ProjectExistsError,
        ProjectNotFoundError,
        addUser as addUserToProject,
        createProject,
        listProjects,
        listUserProjects,
        queryProject,
    )
    from .usersDatabase import addUser, joinProject, login as loginUser, userExists
except ImportError:  # Supports `python server/app.py` from the repository root.
    from dummyHardwareData import DUMMY_HARDWARE, InMemoryHardwareCollection
    from dummyProjectData import DUMMY_PROJECTS, InMemoryProjectCollection
    from hardwareDatabase import (
        HardwareExistsError,
        createHardwareSet,
        listHardwareSets,
        queryHardwareSet,
        requestSpace,
    )
    from projectsDatabase import (
        AlreadyMemberError,
        ProjectExistsError,
        ProjectNotFoundError,
        addUser as addUserToProject,
        createProject,
        listProjects,
        listUserProjects,
        queryProject,
    )
    from usersDatabase import addUser, joinProject, login as loginUser, userExists


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _build_hardware_collection(app):
    """Use MongoDB when configured; otherwise use temporary in-memory data."""
    if app.config["HARDWARE_DATA_SOURCE"] == "mongodb":
        if not app.config["MONGODB_URI"]:
            raise RuntimeError("MONGODB_URI is required when using MongoDB")

        client = MongoClient(
            app.config["MONGODB_URI"],
            serverSelectionTimeoutMS=2500,
        )
        collection = client[app.config["MONGODB_DATABASE"]][
            app.config["MONGODB_HARDWARE_COLLECTION"]
        ]
        try:
            collection.create_index("hwName", unique=True)
        except PyMongoError:
            app.logger.warning("Could not ensure unique index on hwName.")
        return collection, client

    return InMemoryHardwareCollection(DUMMY_HARDWARE), None

def _build_projects_collection(app, mongo_client):
    """Share the hardware MongoDB client when configured; else use memory."""
    if mongo_client is None:
        return InMemoryProjectCollection(DUMMY_PROJECTS)

    collection = mongo_client[app.config["MONGODB_DATABASE"]][
        app.config["MONGODB_PROJECTS_COLLECTION"]
    ]
    try:
        # Enforces unique project IDs even if two requests race.
        collection.create_index("projectId", unique=True)
    except PyMongoError:
        app.logger.warning("Could not ensure unique index on projectId.")
    return collection


def _build_user_collection(app, mongo_client):
    """Create the user collection and enforce unique user IDs."""
    if mongo_client is None:
        return None

    collection = mongo_client[app.config["MONGODB_DATABASE"]][
        app.config["MONGODB_USER_COLLECTION"]
    ]
    try:
        collection.create_index("userId", unique=True)
    except PyMongoError:
        app.logger.warning("Could not ensure unique index on userId.")
    return collection

def create_app(
    config=None,
    hardware_collection=None,
    projects_collection=None,
    user_collection=None,
):
    """Create the Flask application with an injectable hardware collection."""
    app = Flask(__name__)
    default_source = "mongodb" if os.getenv("MONGODB_URI") else "dummy"
    app.config.from_mapping(
        HARDWARE_DATA_SOURCE=os.getenv(
            "HARDWARE_DATA_SOURCE", default_source
        ).lower(),
        MONGODB_URI=os.getenv("MONGODB_URI", ""),
        MONGODB_DATABASE=os.getenv("MONGODB_DATABASE", "HardwareCheckout"),
        MONGODB_HARDWARE_COLLECTION=os.getenv(
            "MONGODB_HARDWARE_COLLECTION", "HardwareSets"
        ),
        MONGODB_PROJECTS_COLLECTION=os.getenv(
            "MONGODB_PROJECTS_COLLECTION", "Projects"
        ),
        MONGODB_USER_COLLECTION=os.getenv("MONGODB_USER_COLLECTION", "Users"),
    )
    if config:
        app.config.update(config)

    mongo_client = None
    if hardware_collection is None:
        hardware_collection, mongo_client = _build_hardware_collection(app)

    if projects_collection is None:
        projects_collection = _build_projects_collection(app, mongo_client)

    if user_collection is None:
        user_collection = _build_user_collection(app, mongo_client)

    app.extensions["hardware_collection"] = hardware_collection
    app.extensions["projects_collection"] = projects_collection
    app.extensions["mongo_client"] = mongo_client

    app.extensions["user_collection"] = user_collection
    

    @app.get("/api/health")
    def health_check():
        if mongo_client is not None:
            try:
                mongo_client.admin.command("ping")
            except PyMongoError:
                return jsonify({"status": "error", "database": "unavailable"}), 503
        return jsonify(
            {
                "status": "ok",
                "hardwareDataSource": app.config["HARDWARE_DATA_SOURCE"],
            }
        )

    @app.get("/api/hardware")
    def get_hardware():
        try:
            hardware = listHardwareSets(app.extensions["hardware_collection"])
        except PyMongoError:
            return jsonify({"error": "Hardware inventory is temporarily unavailable."}), 503
        return jsonify({"hardware": hardware})

    @app.get("/api/hardware/<string:hardware_name>")
    def get_hardware_detail(hardware_name):
        try:
            hardware = queryHardwareSet(
                app.extensions["hardware_collection"], hardware_name
            )
        except PyMongoError:
            return jsonify({"error": "Hardware inventory is temporarily unavailable."}), 503

        if hardware is None:
            return jsonify({"error": "Hardware set not found."}), 404
        return jsonify(hardware)

    @app.post("/api/hardware")
    @app.post("/create_hardware_set")
    def create_hardware_api():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        name = payload.get("name", payload.get("hwSetName"))
        capacity = payload.get("capacity", payload.get("initCapacity"))
        details = {
            key: payload[key]
            for key in ("description", "location", "specifications")
            if key in payload
        }

        try:
            hardware = createHardwareSet(
                app.extensions["hardware_collection"], name, capacity, **details
            )
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        except HardwareExistsError as error:
            return jsonify({"error": str(error)}), 409
        except DuplicateKeyError:
            return jsonify({"error": f"Hardware set '{name}' already exists."}), 409
        except PyMongoError:
            return jsonify({"error": "Hardware inventory is temporarily unavailable."}), 503

        return jsonify(hardware), 201

    @app.post("/api/projects")
    def create_project_api():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        # The creator automatically becomes the project's first member.
        # TODO: take the creator from the signed-in session once Sign In (#2)
        # lands, instead of trusting the request body.
        creator_id = payload.get("userId")
        if not isinstance(creator_id, str) or not creator_id.strip():
            return jsonify({"error": "User ID is required."}), 400
        creator_id = creator_id.strip()

        user_collection = app.extensions["user_collection"]
        try:
            # Check the user first so we never create a project with no
            # real owner. Dummy mode has no user collection, so skip it there.
            if user_collection is not None and not userExists(
                user_collection, creator_id
            ):
                return jsonify({"error": f"User '{creator_id}' was not found."}), 404

            project = createProject(
                app.extensions["projects_collection"],
                payload.get("projectName"),
                payload.get("projectId"),
                payload.get("description", ""),
                creatorId=creator_id,
            )

            # Keep the user's side in sync, same as joining a project.
            if user_collection is not None:
                joinProject(user_collection, creator_id, project["projectId"])

        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        except ProjectExistsError as error:
            return jsonify({"error": str(error)}), 409
        except PyMongoError:
            return jsonify({"error": "Projects are temporarily unavailable."}), 503

        return jsonify(project), 201

    @app.get("/api/projects")
    def get_projects_api():
        try:
            projects = listProjects(app.extensions["projects_collection"])
        except PyMongoError:
            return jsonify({"error": "Projects are temporarily unavailable."}), 503
        return jsonify({"projects": projects}), 200

    @app.get("/api/projects/<string:project_id>")
    def get_project_api(project_id):
        try:
            project = queryProject(app.extensions["projects_collection"], project_id)
        except PyMongoError:
            return jsonify({"error": "Projects are temporarily unavailable."}), 503

        if project is None:
            return jsonify({"error": "Project not found."}), 404
        return jsonify(project)

    @app.post("/api/projects/<string:project_id>/users")
    def add_user_to_project_api(project_id):
        """Add a user to a project (issue #5: Join a Project)."""
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        # TODO: take the user from the signed-in session once Sign In (#2)
        # lands, instead of trusting the request body.
        user_id = payload.get("userId")
        if not isinstance(user_id, str) or not user_id.strip():
            return jsonify({"error": "User ID is required."}), 400
        user_id = user_id.strip()

        user_collection = app.extensions["user_collection"]
        try:
            # Without MongoDB there is no user collection, so local dummy
            # mode skips the "is this a real user" check.
            if user_collection is not None and not userExists(
                user_collection, user_id
            ):
                return jsonify({"error": f"User '{user_id}' was not found."}), 404

            project = addUserToProject(
                app.extensions["projects_collection"], project_id, user_id
            )

            if user_collection is not None:
                joinProject(user_collection, user_id, project["projectId"])
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        except ProjectNotFoundError as error:
            return jsonify({"error": str(error)}), 404
        except AlreadyMemberError as error:
            return jsonify({"error": str(error)}), 409
        except PyMongoError:
            return jsonify({"error": "Projects are temporarily unavailable."}), 503

        return jsonify(project), 200

        
    # Existing team endpoints remain available for parallel development.
    @app.get("/api/users/<string:user_id>/projects")
    def get_user_projects_api(user_id):
        """List every project a user belongs to (issue #6: View My Projects)."""
        # TODO: take the user from the signed-in session once Sign In (#2)
        # lands, instead of trusting the URL.
        user_id = user_id.strip()
        if not user_id:
            return jsonify({"error": "User ID is required."}), 400

        user_collection = app.extensions["user_collection"]
        try:
            # Dummy mode has no user collection, so skip the check there.
            if user_collection is not None and not userExists(
                user_collection, user_id
            ):
                return jsonify({"error": f"User '{user_id}' was not found."}), 404

            projects = listUserProjects(
                app.extensions["projects_collection"], user_id
            )
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        except PyMongoError:
            return jsonify({"error": "Projects are temporarily unavailable."}), 503

        return jsonify({"projects": projects}), 200

    
    # Existing team endpoints remain available for parallel development.
    @app.post("/login")
    def login():
        data = request.get_json(silent=True) or {}

        user_id = str(data.get("userId", "")).strip()
        password = data.get("password", "")

        if not user_id or not password:
            return jsonify({
                "error": "User ID and password are required."
            }), 400

        user_collection = app.extensions["user_collection"]

        if user_collection is None:
            return jsonify({
                "error": "User database is unavailable."
            }), 503

        try:
            user = loginUser(
                user_collection,
                user_id,
                password,
            )
        except PyMongoError:
            return jsonify({
                "error": "User database is temporarily unavailable."
            }), 503

        if user is None:
            return jsonify({
                "error": "Invalid user ID or password."
            }), 401

        return jsonify({"user": user}), 200

    @app.get("/main")
    def main_page():
        return jsonify({})

    @app.post("/join_project")
    def join_project():
        return jsonify({})

    @app.post("/add_user")
    def add_user():
        data = request.get_json(silent=True) or {}

        user_id = str(data.get("userId", "")).strip()
        password = data.get("password", "")
        username = str(data.get("username") or user_id).strip()

        if not user_id or not password:
            return jsonify({
                "error": "User ID and password are required."
            }), 400

        user_collection = app.extensions["user_collection"]

        if user_collection is None:
            return jsonify({
                "error": "User database is unavailable."
            }), 503

        try:
            user = addUser(
                user_collection,
                username,
                user_id,
                password,
            )
        except DuplicateKeyError:
            return jsonify({"error": "User ID already exists."}), 409
        except PyMongoError:
            return jsonify({
                "error": "User database is temporarily unavailable."
            }), 503

        if user is None:
            return jsonify({
                "error": "User ID already exists."
            }), 409

        return jsonify({"user": user}), 201

    @app.post("/get_user_projects_list")
    def get_user_projects_list():
        return jsonify({})

    @app.post("/create_project")
    def create_project():
        return jsonify({})

    @app.post("/get_project_info")
    def get_project_info():
        return jsonify({})

    @app.post("/get_all_hw_names")
    def get_all_hw_names():
        return jsonify({})

    @app.post("/get_hw_info")
    def get_hw_info():
        return jsonify({})

    @app.post("/check_out")
    def check_out():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        hardware_name = payload.get("hardwareName", payload.get("hwSetName"))
        quantity = payload.get("quantity", payload.get("qty"))
        if not isinstance(hardware_name, str) or not hardware_name.strip():
            return jsonify({"error": "Hardware name is required."}), 400

        try:
            hardware = requestSpace(
                app.extensions["hardware_collection"],
                hardware_name.strip(),
                quantity,
            )
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        except PyMongoError:
            return jsonify({"error": "Hardware inventory is temporarily unavailable."}), 503

        if hardware is None:
            return jsonify({"error": "Not enough hardware is available."}), 409
        return jsonify({"hardware": hardware}), 200

    @app.post("/check_in")
    def check_in():
        return jsonify({})

    @app.get("/api/inventory")
    def check_inventory():
        return jsonify({})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
