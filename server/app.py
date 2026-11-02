# Import necessary libraries and modules
import os
import secrets

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, session
from pymongo import MongoClient
from werkzeug.exceptions import NotFound

# Import custom modules for database interactions
import usersDatabase as usersDB
import projectsDatabase as projectsDB
import hardwareDatabase as hardwareDB

load_dotenv()

# Directory holding the built React client (client/dist after `npm run
# build`). In the Docker image the build is copied to a fixed path and
# CLIENT_DIST points at it; locally the default resolves to the sibling
# client/dist, so `npm run build` then `python app.py` serves the real UI
# on one port with no proxy. During `npm run dev` this directory may not
# exist at all -- Vite serves the client and proxies /api here instead.
_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIST = os.environ.get(
    "CLIENT_DIST",
    os.path.normpath(os.path.join(_SERVER_DIR, "..", "client", "dist")),
)

# Initialize a new Flask web application.
#
# static_folder=None disables Flask's built-in static route on purpose.
# That route would otherwise be registered at /<path:filename> and, being
# registered first, would claim every path this app's own catch-all is
# meant to handle -- returning an HTML 404 for unknown /api/... paths and
# breaking the single-page-app fallback. serve_client below does the whole
# job instead.
app = Flask(__name__, static_folder=None)


class MissingDatabaseConfig(RuntimeError):
    """Raised when MONGODB_URI is absent. Maps to HTTP 503.

    Its own class rather than a bare RuntimeError so the error handler
    below can answer with actionable JSON without swallowing unrelated
    RuntimeErrors raised deeper in the app.
    """


@app.errorhandler(MissingDatabaseConfig)
def handleMissingDatabaseConfig(error):
    # A deployed instance with no connection string set must say so in the
    # response, not dump an HTML stack trace: this is the first thing seen
    # when the host is live before MONGODB_URI has been filled in.
    return jsonify({"error": "database_not_configured", "detail": str(error)}), 503

# SECRET_KEY signs the session cookie (TD-02) -- Flask's session is a
# signed cookie, not an opaque token, so without a key no one could trust
# it. Read from the environment (server/.env, same place as MONGODB_URI)
# so it's stable across restarts, meaning existing sessions survive a
# server restart too, not just a page refresh. Falling back to a random
# per-process key rather than raising, unlike MONGODB_URI, because this
# only degrades session persistence (everyone signed in gets signed out
# on the next restart) rather than breaking the app outright.
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    app.secret_key = secrets.token_hex(32)
    print(
        "WARNING: SECRET_KEY is not set -- using a random per-process key. "
        "Existing sessions will not survive a server restart. Set "
        "SECRET_KEY in server/.env for stable sessions."
    )


def getMongoClient():
    """Build a MongoClient from the MONGODB_URI environment variable.

    Raises MissingDatabaseConfig with an actionable message when
    MONGODB_URI is unset -- there is no default connection string
    anywhere in this file.
    """
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise MissingDatabaseConfig(
            "MONGODB_URI is not set. Locally, create a server/.env file with "
            "MONGODB_URI=<your connection string> (see .env.example). In a "
            "deployed environment, set it in the host's environment variables."
        )
    return MongoClient(uri)


# Route for user login
@app.route('/login', methods=['POST'])
def login():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    username = body.get('username')
    userId = body.get('userId')
    password = body.get('password')

    if not username:
        return jsonify({"error": "invalid_input", "field": "username"}), 400
    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400
    if not password:
        return jsonify({"error": "invalid_input", "field": "password"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Attempt to log in the user using the usersDB module
        authenticated = usersDB.login(client, username, userId, password)
    finally:
        # Close the MongoDB connection
        client.close()

    if not authenticated:
        # Deliberately the same error for "wrong password" and "no such
        # user" -- usersDB.login already blurs this at the timing level
        # (ACCT-03); the response must not re-leak it.
        return jsonify({"error": "invalid_credentials"}), 401

    # Establish the session (TD-02) -- a signed, httpOnly cookie the
    # browser sends back automatically. GET /me reads this to restore the
    # signed-in view across a page refresh or a server restart.
    session['userId'] = userId
    session['username'] = username

    # Return a JSON response
    return jsonify({"username": username, "userId": userId}), 200

# Route for restoring a signed-in session (TD-02). The frontend calls
# this once on page load -- before showing anything -- to decide between
# the sign-in form and the resource view, instead of re-prompting for
# credentials on every refresh.
@app.route('/me')
def me():
    userId = session.get('userId')
    username = session.get('username')

    if not userId or not username:
        return jsonify({"error": "not_signed_in"}), 401

    return jsonify({"username": username, "userId": userId}), 200

# Route for signing out (TD-02). Clears the session server-side, so the
# cookie the browser holds is no longer honored by GET /me even if it's
# still sent.
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({}), 200

# Route for the main page (Work in progress)
@app.route('/main')
def mainPage():
    # Extract data from request

    # Connect to MongoDB

    # Fetch user projects using the usersDB module

    # Close the MongoDB connection

    # Return a JSON response
    return jsonify({})

# Route for joining a project
@app.route('/join_project', methods=['POST'])
def join_project():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    userId = body.get('userId')
    projectId = body.get('projectId')

    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400
    if not projectId:
        return jsonify({"error": "invalid_input", "field": "projectId"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Attempt to join the project using the usersDB module
        usersDB.joinProject(client, userId, projectId)
    except projectsDB.ProjectNotFoundError:
        return jsonify({"error": "project_not_found", "field": "projectId"}), 404
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response
    return jsonify({"userId": userId, "projectId": projectId}), 200

# Route for adding a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    username = body.get('username')
    userId = body.get('userId')
    password = body.get('password')

    if not username:
        return jsonify({"error": "invalid_input", "field": "username"}), 400
    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400
    if not password:
        return jsonify({"error": "invalid_input", "field": "password"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Attempt to add the user using the usersDB module
        usersDB.addUser(client, username, userId, password)
    except usersDB.InvalidPasswordError as error:
        return jsonify({"error": "invalid_input", "field": "password", "detail": str(error)}), 400
    except usersDB.UserAlreadyExistsError:
        return jsonify({"error": "user_already_exists", "field": "userId"}), 409
    finally:
        # Close the MongoDB connection
        client.close()

    # Signing up signs you in too (TD-02) -- same session the /login
    # route establishes, so a fresh account doesn't need a separate
    # sign-in immediately after.
    session['userId'] = userId
    session['username'] = username

    # Return a JSON response (never echo the password back, hashed or not)
    return jsonify({"username": username, "userId": userId}), 201

# Route for getting the list of user projects (US-05)
@app.route('/get_user_projects_list', methods=['POST'])
def get_user_projects_list():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    userId = body.get('userId')

    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Fetch the user's projects using the usersDB module
        projects = usersDB.getUserProjectsList(client, userId)
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response
    return jsonify({"projects": projects}), 200

# Route for creating a new project (US-03)
@app.route('/create_project', methods=['POST'])
def create_project():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    projectName = body.get('projectName')
    projectId = body.get('projectId')
    description = body.get('description')
    userId = body.get('userId')

    if not projectName:
        return jsonify({"error": "invalid_input", "field": "projectName"}), 400
    if not projectId:
        return jsonify({"error": "invalid_input", "field": "projectId"}), 400
    if not description:
        return jsonify({"error": "invalid_input", "field": "description"}), 400
    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Attempt to create the project using the projectsDB module
        project = projectsDB.createProject(client, projectName, projectId, description, userId)
    except projectsDB.InvalidProjectInput as error:
        return jsonify({"error": "invalid_input", "field": str(error)}), 400
    except projectsDB.ProjectAlreadyExistsError:
        return jsonify({"error": "project_already_exists", "field": "projectId"}), 409
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response
    return jsonify({"project": project}), 201

# Route for getting project information
@app.route('/get_project_info', methods=['POST'])
def get_project_info():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    projectId = body.get('projectId')
    userId = body.get('userId')

    if not projectId:
        return jsonify({"error": "invalid_input", "field": "projectId"}), 400
    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Fetch project information using the projectsDB module, after
        # confirming the caller actually belongs to it
        projectsDB.assertProjectMember(client, projectId, userId)
        project = projectsDB.queryProject(client, projectId)
    except projectsDB.NotAHouseholdMemberError:
        return jsonify({"error": "not_a_project_member"}), 403
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response
    return jsonify({"project": project}), 200

# Route for viewing a project's hardware-set status (capacity/availability)
@app.route('/api/hardware', methods=['GET'])
def get_hardware_status():
    # Extract data from request
    projectId = request.args.get('projectId')
    userId = request.args.get('userId')

    if not projectId:
        return jsonify({"error": "missing_parameter", "field": "projectId"}), 400
    if not userId:
        return jsonify({"error": "missing_parameter", "field": "userId"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Fetch hardware-set status using the projectsDB module
        hardwareSets = projectsDB.getProjectHardwareStatus(client, projectId, userId)
    except projectsDB.NotAHouseholdMemberError:
        return jsonify({"error": "not_a_project_member"}), 403
    except hardwareDB.ItemNotFoundError:
        return jsonify({"error": "hardware_set_not_found"}), 404
    except hardwareDB.InvalidInventoryInput as error:
        return jsonify({"error": "invalid_input", "field": str(error)}), 400
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response
    return jsonify({"projectId": projectId, "hardwareSets": hardwareSets})

# Route for creating a new hardware set with a starting capacity
@app.route('/api/hardware/create', methods=['POST'])
def create_hardware_set():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    projectId = body.get('projectId')
    userId = body.get('userId')
    hwSetName = body.get('hwSetName')
    capacity = body.get('capacity')

    if not projectId:
        return jsonify({"error": "invalid_input", "field": "projectId"}), 400
    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Attempt to create the hardware set using the projectsDB module
        hardwareSet = projectsDB.createHardwareSet(client, projectId, userId, hwSetName, capacity)
    except projectsDB.NotAHouseholdMemberError:
        return jsonify({"error": "not_a_project_member"}), 403
    except hardwareDB.InvalidInventoryInput as error:
        return jsonify({"error": "invalid_input", "field": str(error)}), 400
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response
    return jsonify({"hardwareSet": hardwareSet}), 201

# Route for checking in units of a hardware set
@app.route('/api/hardware/checkin', methods=['POST'])
def checkin_hardware():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    projectId = body.get('projectId')
    userId = body.get('userId')
    hwSetName = body.get('hwSetName')
    quantity = body.get('quantity')

    if not projectId:
        return jsonify({"error": "invalid_input", "field": "projectId"}), 400
    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Attempt to check in the hardware set using the projectsDB module
        hardwareSet = projectsDB.checkinHardwareSet(
            client, projectId, userId, hwSetName, quantity
        )
    except projectsDB.NotAHouseholdMemberError:
        return jsonify({"error": "not_a_project_member"}), 403
    except hardwareDB.InvalidInventoryInput as error:
        return jsonify({"error": "invalid_input", "field": str(error)}), 400
    except hardwareDB.ItemNotFoundError:
        return jsonify({"error": "hardware_set_not_found"}), 404
    except hardwareDB.CheckinExceedsCheckedOutError as error:
        return jsonify({
            "error": "checkin_exceeds_checked_out",
            "checkedOut": error.checkedOut,
            "requested": error.requested,
        }), 409
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response
    return jsonify({"hardwareSet": hardwareSet}), 200

# Route for checking out units of a hardware set
@app.route('/api/hardware/checkout', methods=['POST'])
def checkout_hardware():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    projectId = body.get('projectId')
    userId = body.get('userId')
    hwSetName = body.get('hwSetName')
    quantity = body.get('quantity')

    if not projectId:
        return jsonify({"error": "invalid_input", "field": "projectId"}), 400
    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Attempt to check out the hardware set using the projectsDB module
        hardwareSet = projectsDB.checkoutHardwareSet(
            client, projectId, userId, hwSetName, quantity
        )
    except projectsDB.NotAHouseholdMemberError:
        return jsonify({"error": "not_a_project_member"}), 403
    except hardwareDB.InvalidInventoryInput as error:
        return jsonify({"error": "invalid_input", "field": str(error)}), 400
    except hardwareDB.ItemNotFoundError:
        return jsonify({"error": "hardware_set_not_found"}), 404
    except hardwareDB.InsufficientStockError as error:
        return jsonify({
            "error": "insufficient_stock",
            "onHand": error.onHand,
            "requested": error.requested,
        }), 409
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response
    return jsonify({"hardwareSet": hardwareSet}), 200

# Route for requesting (reserving) a quantity of a hardware set (SN3)
@app.route('/api/hardware/request', methods=['POST'])
def request_hardware():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    projectId = body.get('projectId')
    userId = body.get('userId')
    userName = body.get('userName')
    hwSetName = body.get('hwSetName')
    quantity = body.get('quantity')

    if not projectId:
        return jsonify({"error": "invalid_input", "field": "projectId"}), 400
    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Attempt to request the hardware set using the projectsDB module
        reservationId, hardwareSet = projectsDB.requestHardwareSet(
            client, projectId, userId, userName, hwSetName, quantity
        )
    except projectsDB.NotAHouseholdMemberError:
        return jsonify({"error": "not_a_project_member"}), 403
    except hardwareDB.InvalidInventoryInput as error:
        return jsonify({"error": "invalid_input", "field": str(error)}), 400
    except hardwareDB.ItemNotFoundError:
        return jsonify({"error": "hardware_set_not_found"}), 404
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response (wire field is "requestId" -- the assignment
    # mockup's own "Request" vocabulary; internal storage stays reservationId)
    return jsonify({"requestId": reservationId, "hardwareSet": hardwareSet}), 201

# Route for releasing a request (reservation) the caller created
@app.route('/api/hardware/release', methods=['POST'])
def release_hardware():
    # Extract data from request
    body = request.get_json(silent=True) or {}
    projectId = body.get('projectId')
    userId = body.get('userId')
    # Wire field is "requestId" (the assignment mockup's own "Request"
    # vocabulary); internal storage/functions still call it reservationId.
    reservationId = body.get('requestId')

    if not projectId:
        return jsonify({"error": "invalid_input", "field": "projectId"}), 400
    if not userId:
        return jsonify({"error": "invalid_input", "field": "userId"}), 400

    # Connect to MongoDB
    client = getMongoClient()

    try:
        # Attempt to release the reservation using the projectsDB module
        hardwareSet = projectsDB.releaseReservation(client, projectId, userId, reservationId)
    except projectsDB.NotAHouseholdMemberError:
        return jsonify({"error": "not_a_project_member"}), 403
    except projectsDB.ReservationNotOwnedError:
        return jsonify({"error": "not_your_reservation"}), 403
    except hardwareDB.ReservationNotFoundError:
        return jsonify({"error": "reservation_not_found"}), 404
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response
    return jsonify({"hardwareSet": hardwareSet}), 200

# ---------------------------------------------------------------------------
# Static client + health check (OPS-01)
#
# The Flask process serves both the JSON API and the built React client, so
# the deployed app is a single service on a single public URL. That is why
# the client's fetch calls use root-relative paths (/api/...) and why no
# CORS configuration is needed anywhere: in production the page and the API
# share an origin.
# ---------------------------------------------------------------------------


# Liveness probe for the host's health check and for any keep-warm pinger.
# Deliberately does NOT touch MongoDB: this must answer even when the
# database is unreachable, otherwise the host restarts a process whose only
# problem is a bad connection string.
@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "clientBuilt": os.path.isdir(CLIENT_DIST)}), 200


# Catch-all serving the built client, including its hashed asset files.
# Only matches what the API routes above did not claim -- Werkzeug prefers
# a literal rule such as /api/hardware over this converter rule, so adding
# a route never gets shadowed by this one.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_client(path):
    # Never let an unmatched /api/... path fall through to index.html: a
    # 200 with an HTML body would make a typo'd endpoint look alive to the
    # client and fail later as a JSON parse error.
    if path.startswith('api/'):
        return jsonify({"error": "not_found", "path": "/" + path}), 404

    index = os.path.join(CLIENT_DIST, 'index.html')
    if not os.path.isfile(index):
        return jsonify({
            "error": "client_not_built",
            "detail": (
                "No built client at {}. Run `npm run build` in client/, or set "
                "CLIENT_DIST to the build output.".format(CLIENT_DIST)
            ),
        }), 503

    # Serve a real build artifact when the path names one; otherwise fall
    # through to index.html so client-side routes survive a page refresh.
    # send_from_directory rejects traversal outside the directory.
    if path:
        try:
            return send_from_directory(CLIENT_DIST, path)
        except NotFound:
            pass

    return send_from_directory(CLIENT_DIST, 'index.html')


# Main entry point for the application
if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5050)))
