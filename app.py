import os
import secrets
import uuid

from flask import (
    Blueprint,
    Flask,
    abort,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from tinydb import Query, TinyDB

DB_PATH = os.environ.get("TODO_DB_PATH", "db.json")
MAX_TITLE_LENGTH = 200
TODOS = Query()


todo_bp = Blueprint("todo", __name__)
db: TinyDB | None = None


def get_db() -> TinyDB:
    if db is None:
        raise RuntimeError("Database is not initialized. Call create_app() first.")
    return db


def _validate_todo_id(todo_id: str) -> str:
    if not todo_id:
        abort(400, description="Todo ID is required.")

    try:
        return uuid.UUID(todo_id, version=4).hex
    except ValueError:
        abort(400, description="Invalid todo ID.")


def _validate_title(raw_title: str | None, field_name: str) -> str:
    title = (raw_title or "").strip()
    if not title:
        abort(400, description=f"{field_name} is required.")
    if len(title) > MAX_TITLE_LENGTH:
        abort(400, description=f"{field_name} must be {MAX_TITLE_LENGTH} characters or fewer.")
    return title


def _ensure_csrf_token() -> str:
    csrf_token = session.get("csrf_token")
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        session["csrf_token"] = csrf_token
    return csrf_token


def _validate_csrf() -> None:
    token_in_session = session.get("csrf_token")
    token_from_form = request.form.get("csrf_token")

    if not token_in_session or not token_from_form:
        abort(400, description="Missing CSRF token.")
    if not secrets.compare_digest(token_in_session, token_from_form):
        abort(400, description="Invalid CSRF token.")


@todo_bp.before_request
def protect_post_requests() -> None:
    if request.method == "POST":
        _validate_csrf()


@todo_bp.before_app_request
def add_csrf_token() -> None:
    g.csrf_token = _ensure_csrf_token()


@todo_bp.route("/")
def list_todos():
    todo_list = get_db().all()
    return render_template("index.html", todo_list=todo_list)


@todo_bp.route("/add", methods=["POST"])
def create_todo():
    title = _validate_title(request.form.get("title"), "Title")
    get_db().insert({"id": uuid.uuid4().hex, "title": title, "complete": False})
    return redirect(url_for("todo.list_todos"))


@todo_bp.route("/update", methods=["POST"])
def update_todo():
    updated_title = _validate_title(request.form.get("title"), "Updated title")
    todo_id = _validate_todo_id(request.form.get("todo_id") or "")

    updated_items = get_db().update({"title": updated_title}, TODOS.id == todo_id)
    if not updated_items:
        abort(404, description=f"Todo '{todo_id}' was not found.")

    return redirect(url_for("todo.list_todos"))


@todo_bp.route("/delete/<string:todo_id>", methods=["POST"])
def delete_todo(todo_id: str):
    normalized_id = _validate_todo_id(todo_id)
    removed_items = get_db().remove(TODOS.id == normalized_id)
    if not removed_items:
        abort(404, description=f"Todo '{normalized_id}' was not found.")

    return redirect(url_for("todo.list_todos"))


@todo_bp.route("/complete/<string:todo_id>", methods=["POST"])
def complete_todo(todo_id: str):
    normalized_id = _validate_todo_id(todo_id)
    updated_items = get_db().update({"complete": True}, TODOS.id == normalized_id)
    if not updated_items:
        abort(404, description=f"Todo '{normalized_id}' was not found.")

    return redirect(url_for("todo.list_todos"))


def create_app() -> Flask:
    flask_app = Flask(__name__)
    flask_app.config["TODO_DB_PATH"] = DB_PATH
    flask_app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

    # Set a stable secret key for session signing (required for CSRF tokens).
    flask_app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

    flask_app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
    )

    @flask_app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    global db
    db = TinyDB(flask_app.config["TODO_DB_PATH"])

    flask_app.register_blueprint(todo_bp)
    return flask_app


app = create_app()

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)
