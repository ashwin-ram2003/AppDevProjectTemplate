"""Shared runtime configuration.

Single source of truth for the database name. It lives here rather than in
each data-access module because those modules previously each declared
their own default: usersDatabase defaulted to one database and
hardwareDatabase to another, so with MONGODB_DB unset the app silently
wrote users to one database and projects/hardware sets to a second. Logins
would succeed while every project membership check failed, because the two
halves of the app were looking at different data.

Every module that opens a database reads DB_NAME from here, so the default
can only ever be defined in one place.
"""

import os

# Database inside the MongoDB cluster. Override per environment with
# MONGODB_DB; the default is what local development and the deployed
# service both use unless told otherwise.
DB_NAME = os.environ.get("MONGODB_DB", "HaaSResourceManager")
