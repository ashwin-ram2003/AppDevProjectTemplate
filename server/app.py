# Import necessary libraries and modules
from bson.objectid import ObjectId
from flask import Flask, request, jsonify
from pymongo import MongoClient

# Import custom modules for database interactions
import usersDatabase as usersDB
import projectsDatabase as projectsDB
import hardwareDatabase as hardwareDB

# Define the MongoDB connection string
MONGODB_SERVER = "mongodb+srv://Admin:xshfdkfdfgdf6iXg@cluster0.gqr93yv.mongodb.net/?appName=Cluster0"

# Initialize a new Flask web application
app = Flask(__name__)

# Helper function, checks if MongoDB document contains ObjectId in '_id'
def clean_doc(doc):
    if doc is None:
        return None
    doc = dict(doc)
    if isinstance(doc.get('_id'), ObjectId):
        doc['_id'] = str(doc['_id'])
    return doc

# Helper function, parse a positive number from request data
def parse_qty(value):
    try:
        qty = int(value)
    except (TypeError, ValueError):
        return None
    return qty if qty > 0 else None

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    # Get specific data
    username = data.get('username')
    userId = data.get('userId')
    password = data.get('password')

    # Check for errors
    if not username or not userId or not password:
        return jsonify({'success': False,'message': 'username, userId, and password are required'}), 400

    client = None

    # Connect to MongoDB
    try:
        client = MongoClient(MONGODB_SERVER)
        # Attempt to log in the user using the usersDB module
        success = usersDB.login(client, username, userId, password)
    # Catch error
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()
    # Return a JSON response
    if success:
        return jsonify({'success': True, 'message': 'Login successful','username': username, 'userId': userId}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# Route for the main page (Work in progress)
@app.route('/main')
def mainPage():
    # Extract data from request (GET, so it comes from the query string: /main?userId=jb123)
    userId = request.args.get('userId')

    if not userId:
        return jsonify({'success': False, 'message': 'userId is required'}), 400

    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)

        # Fetch user projects using the usersDB module
        projects = usersDB.getUserProjectsList(client, userId)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()

    # Return a JSON response
    if projects is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'userId': userId, 'projects': projects}), 200

# Route for joining a project
@app.route('/join_project', methods=['POST'])
def join_project():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    userId = data.get('userId')
    projectId = data.get('projectId')

    if not userId or not projectId:
        return jsonify({'success': False,
                        'message': 'userId and projectId are required'}), 400

    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)

        # Attempt to join the project using the usersDB module
        success = usersDB.joinProject(client, userId, projectId)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()

    # Return a JSON response
    if success:
        return jsonify({'success': True,
                        'message': f'Joined project {projectId}'}), 200
    return jsonify({'success': False,
                    'message': 'Could not join project (check that the project ID exists)'}), 400

# Route for adding a new user
@app.route('/add_user', methods=['POST'])
def add_user():
     # Extract data from request
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    userId = data.get('userId')
    password = data.get('password')

    if not username or not userId or not password:
        return jsonify({'success': False,
                        'message': 'username, userId, and password are required'}), 400

    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)

        # Attempt to add the user using the usersDB module
        success = usersDB.addUser(client, username, userId, password)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()

    # Return a JSON response
    if success:
        return jsonify({'success': True, 'message': 'Account created',
                        'username': username, 'userId': userId}), 201
    return jsonify({'success': False, 'message': 'That userId is already taken'}), 409

# Route for getting the list of user projects
@app.route('/get_user_projects_list', methods=['POST'])
def get_user_projects_list():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    userId = data.get('userId')
 
    if not userId:
        return jsonify({'success': False, 'message': 'userId is required'}), 400
 
    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)
 
        # Fetch the user's projects using the usersDB module
        projects = usersDB.getUserProjectsList(client, userId)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()
 
    # Return a JSON response
    if projects is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'projects': projects}), 200

# Route for creating a new project
@app.route('/create_project', methods=['POST'])
def create_project():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    projectName = data.get('projectName')
    projectId = data.get('projectId')
    description = data.get('description', '')
    userId = data.get('userId')  # optional: the creator is added to the project
 
    if not projectName or not projectId:
        return jsonify({'success': False,
                        'message': 'projectName and projectId are required'}), 400
 
    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)
 
        # Attempt to create the project using the projectsDB module
        success = projectsDB.createProject(client, projectName, projectId, description)
 
        # If created and we know who made it, add the creator as a member
        if success and userId:
            usersDB.joinProject(client, userId, projectId)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()
 
    # Return a JSON response
    if success:
        return jsonify({'success': True, 'message': 'Project created',
                        'projectId': projectId}), 201
    return jsonify({'success': False, 'message': 'That projectId is already taken'}), 409

# Route for getting project information
@app.route('/get_project_info', methods=['POST'])
def get_project_info():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    projectId = data.get('projectId')
 
    if not projectId:
        return jsonify({'success': False, 'message': 'projectId is required'}), 400
 
    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)
 
        # Fetch project information using the projectsDB module
        project = projectsDB.queryProject(client, projectId)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()
 
    # Return a JSON response
    if project is None:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    return jsonify({'success': True, 'project': clean_doc(project)}), 200

# Route for getting all hardware names
@app.route('/get_all_hw_names', methods=['POST'])
def get_all_hw_names():
    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)
 
        # Fetch all hardware names using the hardwareDB module
        hw_names = hardwareDB.getAllHwNames(client)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()
 
    # Return a JSON response
    return jsonify({'success': True, 'hwNames': hw_names or []}), 200

# Route for getting hardware information
@app.route('/get_hw_info', methods=['POST'])
def get_hw_info():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    hwSetName = data.get('hwSetName')
 
    if not hwSetName:
        return jsonify({'success': False, 'message': 'hwSetName is required'}), 400
 
    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)
 
        # Fetch hardware set information using the hardwareDB module
        hw_set = hardwareDB.queryHardwareSet(client, hwSetName)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()
 
    # Return a JSON response
    if hw_set is None:
        return jsonify({'success': False, 'message': 'Hardware set not found'}), 404
    return jsonify({'success': True,
                    'hwName': hw_set.get('hwName'),
                    'capacity': hw_set.get('capacity'),
                    'availability': hw_set.get('availability')}), 200

# Route for checking out hardware
@app.route('/check_out', methods=['POST'])
def check_out():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    projectId = data.get('projectId')
    hwSetName = data.get('hwSetName')
    userId = data.get('userId')
    qty = parse_qty(data.get('qty'))
 
    if not projectId or not hwSetName or not userId:
        return jsonify({'success': False,
                        'message': 'projectId, hwSetName, and userId are required'}), 400
    if qty is None:
        return jsonify({'success': False,
                        'message': 'qty must be a positive whole number'}), 400
 
    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)
 
        # Attempt to check out the hardware using the projectsDB module
        success = projectsDB.checkOutHW(client, projectId, hwSetName, qty, userId)
 
        # Grab the updated availability so the UI can refresh immediately
        hw_set = hardwareDB.queryHardwareSet(client, hwSetName)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()
 
    availability = hw_set.get('availability') if hw_set else None
 
    # Return a JSON response
    if success:
        return jsonify({'success': True,
                        'message': f'Checked out {qty} unit(s) of {hwSetName}',
                        'availability': availability}), 200
    return jsonify({'success': False,
                    'message': f'Request exceeds available units of {hwSetName}',
                    'availability': availability}), 400

# Route for checking in hardware
@app.route('/check_in', methods=['POST'])
def check_in():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    projectId = data.get('projectId')
    hwSetName = data.get('hwSetName')
    userId = data.get('userId')
    qty = parse_qty(data.get('qty'))
 
    if not projectId or not hwSetName or not userId:
        return jsonify({'success': False,
                        'message': 'projectId, hwSetName, and userId are required'}), 400
    if qty is None:
        return jsonify({'success': False,
                        'message': 'qty must be a positive whole number'}), 400
 
    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)
 
        # Attempt to check in the hardware using the projectsDB module
        success = projectsDB.checkInHW(client, projectId, hwSetName, qty, userId)
 
        # Grab the updated availability so the UI can refresh immediately
        hw_set = hardwareDB.queryHardwareSet(client, hwSetName)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()
 
    availability = hw_set.get('availability') if hw_set else None
 
    # Return a JSON response
    if success:
        return jsonify({'success': True,
                        'message': f'Checked in {qty} unit(s) of {hwSetName}',
                        'availability': availability}), 200
    return jsonify({'success': False,
                    'message': 'Cannot check in more units than the project has checked out',
                    'availability': availability}), 400

# Route for creating a new hardware set
@app.route('/create_hardware_set', methods=['POST'])
def create_hardware_set():
    # Extract data from request
    data = request.get_json(silent=True) or {}
    hwSetName = data.get('hwSetName')
    initCapacity = parse_qty(data.get('initCapacity'))
 
    if not hwSetName:
        return jsonify({'success': False, 'message': 'hwSetName is required'}), 400
    if initCapacity is None:
        return jsonify({'success': False,
                        'message': 'initCapacity must be a positive whole number'}), 400
 
    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)
 
        # Attempt to create the hardware set using the hardwareDB module
        success = hardwareDB.createHardwareSet(client, hwSetName, initCapacity)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()
 
    # Return a JSON response
    if success:
        return jsonify({'success': True,
                        'message': f'Hardware set {hwSetName} created',
                        'capacity': initCapacity}), 201
    return jsonify({'success': False,
                    'message': 'A hardware set with that name already exists'}), 409

# Route for checking the inventory of projects
@app.route('/api/inventory', methods=['GET'])
def check_inventory():
    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_SERVER)
 
        # Fetch all projects
        projects = [clean_doc(p) for p in client['HardwareCheckout']['Projects'].find({})]
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'}), 500
    finally:
        # Close the MongoDB connection
        if client is not None:
            client.close()
 
    # Return a JSON response
    return jsonify({'success': True, 'projects': projects}), 200

# Main entry point for the application
if __name__ == '__main__':
    app.run()

