# Import necessary libraries and modules
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

'''
Structure of Hardware Set entry:
HardwareSet = {
    'hwName': hwSetName,
    'capacity': initCapacity,
    'availability': initCapacity
}
'''
# Database and collection names
DB_NAME = 'HardwareCheckout'
COLLECTION = 'HardwareSets'

# Helper function: get's the hardware collection from client
def getCollection(client):
    return client[DB_NAME][COLLECTION]

# Helper function: check if number is an int
def isInt(value):
    return isinstance(value, int) and not isinstance(value, bool)

# Function to create a new hardware set
def createHardwareSet(client, hwSetName, initCapacity):
    # Create a new hardware set in the database
    # Check if name is invalid or the name already exist
    if not hwSetName or not isInt(initCapacity) or initCapacity < 0:
        return False

    hw = getCollection(client)

    # create the index so that two sets can't share a name
    hw.create_index('hwName', unique=True)

    try:
        hw.insert_one({
            'hwName': hwSetName,
            'capacity': initCapacity,
            'availability': initCapacity
        })
    except DuplicateKeyError:
        return False
    return True

# Function to query a hardware set by its name
def queryHardwareSet(client, hwSetName):
    # Query and return a hardware set from the database
    hw = getCollection(client)
    return hw.find_one({'hwName': hwSetName})

# Function to update the availability of a hardware set
def updateAvailability(client, hwSetName, newAvailability):
    # Update the availability of an existing hardware set
    # Check if the set doesn't exist or the value is invalid
    if not isInt(newAvailability) or newAvailability < 0:
        return False

    hw = getCollection(client)
    hw_set = hw.find_one({'hwName': hwSetName})
    if hw_set is None or newAvailability > hw_set['capacity']:
        return False
 
    result = hw.update_one(
        {'hwName': hwSetName},
        {'$set': {'availability': newAvailability}}
    )
    return result.matched_count == 1

# Function to request space from a hardware set
def requestSpace(client, hwSetName, amount):
    # Request a certain amount of hardware and update availability
    # Check if any space is available
    if not isInt(amount) or amount <= 0:
        return False
 
    hw = getCollection(client)
 
    # Check and decrement in one atomic step so two simultaneous
    # requests can never oversell the set
    result = hw.update_one(
        {'hwName': hwSetName, 'availability': {'$gte': amount}},
        {'$inc': {'availability': -amount}}
    )
    return result.modified_count == 1

# Function to get all hardware set names
def getAllHwNames(client):
    # Get and return a list of all hardware set names
    hw = getCollection(client)
    return [doc['hwName'] for doc in hw.find({}, {'hwName': 1, '_id': 0})]

