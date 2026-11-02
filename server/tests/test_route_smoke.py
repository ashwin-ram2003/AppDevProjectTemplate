"""Every registered route survives an empty request (TD-09).

Walks app.url_map instead of a hand-written list, so routes added later
(Track A's login, project create/join, and so on) are covered the moment
they're registered. An empty body or missing query string is the most
common malformed request there is; the right answer is a 4xx, never an
unhandled exception. With app.testing on, an exception raised inside a
route surfaces here as a test error with its full traceback.
"""

import re

import pytest

import app as flask_app_module

_CONVERTER = re.compile(r"<(?:[a-z]+:)?([a-zA-Z_]+)>")


def _registeredEndpoints():
    cases = []
    for rule in flask_app_module.app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        url = _CONVERTER.sub("smoke-test", rule.rule)
        for method in sorted((rule.methods or set()) & {"GET", "POST"}):
            cases.append(pytest.param(method, url, id="{} {}".format(method, rule.rule)))
    return cases


@pytest.fixture
def builtClient(tmp_path, monkeypatch):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html>")
    monkeypatch.setattr(flask_app_module, "CLIENT_DIST", str(dist))


def test_the_route_table_is_not_empty():
    """Guards the parametrization below against silently testing nothing."""
    assert len(_registeredEndpoints()) >= 10


@pytest.mark.parametrize("method,url", _registeredEndpoints())
def test_empty_request_never_errors(api, builtClient, method, url):
    if method == "GET":
        response = api.get(url)
    else:
        response = api.post(url, json={})

    assert response.status_code < 500, (method, url, response.get_data(as_text=True))
