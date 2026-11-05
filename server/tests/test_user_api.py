from werkzeug.security import generate_password_hash

from server.app import create_app


class FakeUserCollection:
    def __init__(self, users=None):
        self.users = users or []

    def find_one(self, query):
        user_id = query.get("userId")

        for user in self.users:
            if user.get("userId") == user_id:
                return user

        return None


def make_client():
    users = [
        {
            "username": "testuser",
            "userId": "testuser",
            "password": generate_password_hash("password123"),
            "projects": [],
        }
    ]

    app = create_app(
        {"TESTING": True},
        user_collection=FakeUserCollection(users),
    )

    return app.test_client()


def test_login_success():
    client = make_client()

    response = client.post(
        "/login",
        json={
            "userId": "testuser",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["user"]["userId"] == "testuser"


def test_login_wrong_password():
    client = make_client()

    response = client.post(
        "/login",
        json={
            "userId": "testuser",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid user ID or password."


def test_login_missing_fields():
    client = make_client()

    response = client.post(
        "/login",
        json={},
    )

    assert response.status_code == 400