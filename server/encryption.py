# Import necessary libraries and modules
import hashlib
import hmac
import os

# Secret key for hashing user IDs (don't change it once users exist)
USERID_SECRET = os.environ.get("USERID_SECRET", "dev-only-userid-secret").encode()

# Function to hash a userId before it goes into the database
def protect_user_id(userId):
    return hmac.new(USERID_SECRET, userId.encode(), hashlib.sha256).hexdigest()
