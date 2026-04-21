# Flask Todo App

A lightweight **Flask-based Todo web application** that lets users create, update, complete, and delete tasks through a single-page interface.

This project uses:
- **Flask** for routing and server-side rendering
- **TinyDB** for simple file-based data persistence (`db.json`)
- **Jinja2 templates** for dynamic HTML rendering
- Basic JavaScript and W3.CSS/Font Awesome for interactivity and styling

---

## Project Overview

The application is intentionally minimal: it stores todo items as JSON records and renders them in a single HTML template.

Each todo item has:
- `id` (random integer from 0–1000)
- `title` (task text)
- `complete` (boolean status)

### Key Features
- Add new tasks
- Mark tasks as complete
- Edit existing task text using a popup form
- Delete tasks
- Persist tasks to local JSON file (`db.json`)

---

## Project Structure

```text
flask-todo-app/
├── app.py                 # Flask application and routes
├── db.json                # TinyDB JSON database file
├── templates/
│   └── index.html         # Main UI template
├── screenshot/            # Example UI screenshots
└── README.md
```

---

## How the Application Works

## 1) Backend (`app.py`)

### App initialization
- Creates a Flask app instance.
- Initializes TinyDB with `db.json` as the storage backend.

### Routes

#### `GET /`
Loads all todo records from TinyDB and renders `templates/index.html` with `todo_list`.

#### `POST /add`
- Reads `title` from form input.
- Inserts a new record:
  - random `id`
  - provided `title`
  - `complete=False`
- Redirects back to `/`.

#### `POST /update`
- Reads:
  - `inputField` (new task text)
  - `hiddenField` (task id)
- Updates matching todo record title.
- Redirects back to `/`.

#### `GET /delete/<todo_id>`
- Deletes the record matching `todo_id`.
- Redirects back to `/`.

#### `GET /complete/<todo_id>`
- Sets `complete=True` for matching task.
- Redirects back to `/`.

### Run mode
When `app.py` is run directly, Flask starts in debug mode (`debug=True`).

---

## 2) Frontend Template (`templates/index.html`)

The UI is rendered from one template and includes:

- A task input form posting to `/add`
- A loop over `todo_list` to display each item
- Different visual styles for incomplete vs complete tasks
- Action buttons per task:
  - complete (`/complete/<id>`)
  - edit (opens popup)
  - delete (`/delete/<id>`)
- A popup form posting updates to `/update`
- A live date/time display updated via JavaScript every second

### JavaScript responsibilities
- Populate and open the edit popup (`openPopup`)
- Fill hidden id field and editable title field
- Provide helper to close popup (`closePopup`)
- Keep current date/time displayed

---

## Requirements

- Python 3.8+
- `pip`

Python packages:
- `flask`
- `tinydb`

---

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd flask-todo-app
   ```

2. **(Recommended) Create and activate a virtual environment**

   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Windows (PowerShell):
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```bash
   pip install flask tinydb
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

5. **Open in browser**
   Visit:
   ```
   http://127.0.0.1:5000/
   ```

---

## Usage Guide

1. Enter a task in **“Add Your Task Here”** and click `+`.
2. Click the **check icon** to mark a task complete.
3. Click the **pencil icon** to edit task text in the popup, then submit **Update**.
4. Click the **trash icon** to delete a task.

Completed tasks are visually highlighted and displayed with strikethrough text.

---

## Data Storage Notes

- All data is stored in `db.json` via TinyDB.
- The app does not include authentication or multi-user separation.
- IDs are generated randomly (`0–1000`), so collisions are possible in rare cases.

---

## Development Notes and Improvements

Potential enhancements:
- Use guaranteed-unique IDs (UUID or TinyDB document IDs)
- Add input validation (prevent empty task titles)
- Add ability to unmark completed tasks
- Convert destructive GET routes (`delete`, `complete`) to POST for safer semantics
- Add `requirements.txt` and automated tests
- Close popup on outside click / Esc key and wire close button behavior explicitly

---

## Screenshots

- Home: `screenshot/Home.png`
- Task creation: `screenshot/Task_creation.png`
- Task update: `screenshot/UpdateTodo.png`
- Update/Delete flow: `screenshot/update_delete.png`

---

## License

No license file is currently included in this repository. Add a `LICENSE` file if you plan to distribute or open-source the project.
