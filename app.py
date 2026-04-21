import os
import uuid

from flask import (
    Blueprint,
    Flask,
    abort,
    redirect,
    render_template,
    request,
    url_for,
)
from tinydb import Query, TinyDB

DB_PATH = os.environ.get("TODO_DB_PATH", "db.json")
TODOS = Query()

todo_bp = Blueprint("todo", __name__)
db: TinyDB | None = None


def get_db() -> TinyDB:
    if db is None:
        raise RuntimeError("Database is not initialized. Call create_app() first.")
    return db


@todo_bp.route("/")
def list_todos():
    todo_list = get_db().all()
    return render_template("index.html", todo_list=todo_list)


@todo_bp.route("/add", methods=["POST"])
def create_todo():
    title = (request.form.get("title") or "").strip()
    if not title:
        abort(400, description="Title is required.")

    get_db().insert({"id": uuid.uuid4().hex, "title": title, "complete": False})
    return redirect(url_for("todo.list_todos"))


@todo_bp.route("/update", methods=["POST"])
def update_todo():
    updated_title = (request.form.get("title") or "").strip()
    todo_id = request.form.get("todo_id")

    if not todo_id:
        abort(400, description="Todo ID is required.")
    if not updated_title:
        abort(400, description="Updated title is required.")

    updated_items = get_db().update({"title": updated_title}, TODOS.id == todo_id)
    if not updated_items:
        abort(404, description=f"Todo '{todo_id}' was not found.")

    return redirect(url_for("todo.list_todos"))


@todo_bp.route("/delete/<string:todo_id>", methods=["POST"])
def delete_todo(todo_id: str):
    removed_items = get_db().remove(TODOS.id == todo_id)
    if not removed_items:
        abort(404, description=f"Todo '{todo_id}' was not found.")

    return redirect(url_for("todo.list_todos"))


@todo_bp.route("/complete/<string:todo_id>", methods=["POST"])
def complete_todo(todo_id: str):
    updated_items = get_db().update({"complete": True}, TODOS.id == todo_id)
    if not updated_items:
        abort(404, description=f"Todo '{todo_id}' was not found.")

    return redirect(url_for("todo.list_todos"))


def create_app() -> Flask:
    flask_app = Flask(__name__)
    flask_app.config["TODO_DB_PATH"] = DB_PATH

    global db
    db = TinyDB(flask_app.config["TODO_DB_PATH"])

    flask_app.register_blueprint(todo_bp)
    return flask_app


app = create_app()

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)
