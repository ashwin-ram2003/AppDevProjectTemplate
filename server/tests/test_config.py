"""Guards the single database-name source (server/config.py).

These exist because the modules once declared their own defaults and
drifted apart: usersDatabase defaulted to one database name and
hardwareDatabase to another, so with MONGODB_DB unset the app wrote users
to one database and projects/hardware sets to a second. Nothing failed
loudly -- a login succeeded and then every project membership check said
the user belonged to no project, because the two halves of the app were
reading different data.

The failure is invisible to any test that seeds and reads through a single
module, which is why it survived a green suite. These assert the property
directly instead.

Anything that needs a different environment runs in a subprocess.
Reloading these modules in-process is not a safe alternative: reload
rebinds the module's classes, so exception types captured by other
already-imported modules stop matching the ones a reloaded module raises,
and unrelated tests start failing with confusing errors.
"""

import pathlib
import subprocess
import sys


SERVER_DIR = pathlib.Path(__file__).resolve().parent.parent

MODULES_OPENING_A_DATABASE = ("usersDatabase", "hardwareDatabase")

_REPORT_DB_NAMES = (
    "import sys; sys.path.insert(0, {serverDir!r});"
    "import usersDatabase, hardwareDatabase;"
    "print(usersDatabase.DB_NAME); print(hardwareDatabase.DB_NAME)"
)


def _dbNamesInSubprocess(env=None):
    """Return each module's DB_NAME as seen by a fresh interpreter."""
    result = subprocess.run(
        [sys.executable, "-c", _REPORT_DB_NAMES.format(serverDir=str(SERVER_DIR))],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return result.stdout.split()


def test_every_module_agrees_on_the_database_name():
    names = _dbNamesInSubprocess()

    assert len(set(names)) == 1, (
        "modules disagree on which database to open: {}".format(
            dict(zip(MODULES_OPENING_A_DATABASE, names))
        )
    )


def test_database_name_follows_the_environment():
    import os

    env = dict(os.environ, MONGODB_DB="AgreementProbe")

    names = _dbNamesInSubprocess(env=env)

    assert set(names) == {"AgreementProbe"}, (
        "MONGODB_DB did not reach every module: {}".format(
            dict(zip(MODULES_OPENING_A_DATABASE, names))
        )
    )


def test_modules_do_not_declare_their_own_default():
    """A module that reads MONGODB_DB itself can drift from config.py again.

    config.py is the only place allowed to read that key.
    """
    offenders = [
        moduleName
        for moduleName in MODULES_OPENING_A_DATABASE
        if "MONGODB_DB" in (SERVER_DIR / "{}.py".format(moduleName)).read_text()
    ]

    assert not offenders, (
        "these modules read MONGODB_DB directly instead of importing DB_NAME "
        "from config.py, which is how the two defaults drifted apart "
        "before: {}".format(offenders)
    )
