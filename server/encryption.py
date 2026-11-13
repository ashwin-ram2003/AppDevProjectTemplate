# Import necessary libraries and modules
import hashlib
import hmac
import os

# Secret key for hashing user IDs (don't change it once users exist)
USERID_SECRET_VALUE = os.environ.get("USERID_SECRET")
if not USERID_SECRET_VALUE:
    if os.environ.get("USE_MOCK_DB") != "1" and os.environ.get("FLASK_ENV") != "development":
        raise RuntimeError("USERID_SECRET must be configured outside local development")
    USERID_SECRET_VALUE = "local-development-userid-secret"
USERID_SECRET = USERID_SECRET_VALUE.encode()

# Function to hash a userId before it goes into the database
def protect_user_id(userId):
    return hmac.new(USERID_SECRET, userId.encode(), hashlib.sha256).hexdigest()
