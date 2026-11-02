"""The deployed app is one Flask process serving both the JSON API and the
built React client (TD-08). These tests pin how that split behaves:
/healthz for the host's health check, real build files served as files,
client-side routes falling back to index.html, and /api/... paths never
falling back to HTML.
"""

import pytest

import app as flask_app_module

INDEX_HTML = "<!doctype html><title>HaaS</title><div id='root'></div>"


@pytest.fixture
def web(monkeypatch):
    """A test client whose database access fails loudly, so any test here
    that accidentally reaches MongoDB shows up as an error.
    """

    def noDatabase():
        raise AssertionError("this route must not touch the database")

    monkeypatch.setattr(flask_app_module, "getMongoClient", noDatabase)
    flask_app_module.app.testing = True
    return flask_app_module.app.test_client()


@pytest.fixture
def builtClient(tmp_path, monkeypatch):
    """A fake `npm run build` output: index.html plus one hashed asset, and
    a file just outside the build directory that must never be served.
    """
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text(INDEX_HTML)
    (dist / "assets" / "index-abc123.js").write_text("console.log('built');")
    (tmp_path / "secret.txt").write_text("outside the build directory")
    monkeypatch.setattr(flask_app_module, "CLIENT_DIST", str(dist))
    return dist


@pytest.fixture
def unbuiltClient(tmp_path, monkeypatch):
    monkeypatch.setattr(flask_app_module, "CLIENT_DIST", str(tmp_path / "no-build-here"))


# --- /healthz ---------------------------------------------------------------


def test_healthz_is_ok_without_touching_the_database(web, builtClient):
    response = web.get("/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "clientBuilt": True}


def test_healthz_reports_a_missing_client_build_but_stays_200(web, unbuiltClient):
    """A missing build is worth reporting, but it isn't a reason for the
    host to restart the process, so the status code stays 200.
    """
    response = web.get("/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "clientBuilt": False}


# --- serving the client -----------------------------------------------------


def test_root_serves_the_built_index(web, builtClient):
    response = web.get("/")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert response.get_data(as_text=True) == INDEX_HTML


def test_build_assets_are_served_as_files(web, builtClient):
    response = web.get("/assets/index-abc123.js")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "console.log('built');"


@pytest.mark.parametrize("clientRoute", ["/dashboard", "/projects/P1", "/login"])
def test_client_side_routes_fall_back_to_index_so_refresh_works(web, builtClient, clientRoute):
    response = web.get(clientRoute)

    assert response.status_code == 200
    assert response.get_data(as_text=True) == INDEX_HTML


def test_paths_outside_the_build_directory_are_never_served(web, builtClient):
    response = web.get("/../secret.txt")

    assert "outside the build directory" not in response.get_data(as_text=True)


@pytest.mark.parametrize("path", ["/api/nope", "/api/hardware/typo", "/api/"])
def test_unknown_api_paths_are_json_404s_not_the_index(web, builtClient, path):
    """Falling back to index.html here would turn a typo'd endpoint into a
    200 with an HTML body, which the client would only discover later as
    a confusing JSON parse error.
    """
    response = web.get(path)

    assert response.status_code == 404
    assert response.get_json() == {"error": "not_found", "path": path}


def test_missing_build_is_an_actionable_503(web, unbuiltClient):
    response = web.get("/")

    assert response.status_code == 503
    body = response.get_json()
    assert body["error"] == "client_not_built"
    assert "npm run build" in body["detail"]
