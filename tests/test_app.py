import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

import app as todo_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test_db.json"

    if todo_app.db is not None:
        todo_app.db.close()

    todo_app.DB_PATH = str(db_path)
    flask_app = todo_app.create_app()
    flask_app.config.update(TESTING=True)

    yield flask_app

    if todo_app.db is not None:
        todo_app.db.close()
        todo_app.db = None


@pytest.fixture()
def client(app):
    return app.test_client()


def _csrf_token(client):
    client.get("/")
    with client.session_transaction() as session:
        return session["csrf_token"]


def test_main_page_loads_successfully(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Todo" in response.data


def test_can_add_new_task(client):
    csrf_token = _csrf_token(client)

    response = client.post(
        "/add",
        data={"title": "Write tests", "csrf_token": csrf_token},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Write tests" in response.data


def test_can_delete_existing_task(client):
    task_id = uuid.uuid4().hex
    todo_app.get_db().insert({"id": task_id, "title": "Delete me", "complete": False})
    csrf_token = _csrf_token(client)

    response = client.post(f"/delete/{task_id}", data={"csrf_token": csrf_token}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Delete me" not in response.data
