# Import necessary libraries and modules
import os

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
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

    # Connect to MongoDB

    # Attempt to log in the user using the usersDB module

    # Close the MongoDB connection

    # Return a JSON response
    return jsonify({})

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

    # Connect to MongoDB

    # Attempt to join the project using the usersDB module

    # Close the MongoDB connection

    # Return a JSON response
    return jsonify({})

# Route for adding a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    # Extract data from request

    # Connect to MongoDB

    # Attempt to add the user using the usersDB module

    # Close the MongoDB connection

    # Return a JSON response
    return jsonify({})

# Route for getting the list of user projects
@app.route('/get_user_projects_list', methods=['POST'])
def get_user_projects_list():
    # Extract data from request

    # Connect to MongoDB

    # Fetch the user's projects using the usersDB module

    # Close the MongoDB connection

    # Return a JSON response
    return jsonify({})

# Route for creating a new project
@app.route('/create_project', methods=['POST'])
def create_project():
    # Extract data from request

    # Connect to MongoDB

    # Attempt to create the project using the projectsDB module

    # Close the MongoDB connection

    # Return a JSON response
    return jsonify({})

# Route for getting project information
@app.route('/get_project_info', methods=['POST'])
def get_project_info():
    # Extract data from request

    # Connect to MongoDB

    # Fetch project information using the projectsDB module

    # Close the MongoDB connection

    # Return a JSON response
    return jsonify({})

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
    except projectsDB.NotAProjectMemberError:
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
    except projectsDB.NotAProjectMemberError:
        return jsonify({"error": "not_a_project_member"}), 403
    except hardwareDB.InvalidInventoryInput as error:
        return jsonify({"error": "invalid_input", "field": str(error)}), 400
    except hardwareDB.ItemNotFoundError:
        return jsonify({"error": "hardware_set_not_found"}), 404
    finally:
        # Close the MongoDB connection
        client.close()

    # Return a JSON response
    return jsonify({"hardwareSet": hardwareSet}), 201

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
    except projectsDB.NotAProjectMemberError:
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
    except hardwareDB.ConcurrentModificationError:
        return jsonify({"error": "concurrent_modification"}), 409
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
    except projectsDB.NotAProjectMemberError:
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
    except projectsDB.NotAProjectMemberError:
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
