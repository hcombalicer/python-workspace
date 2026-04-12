"""
Shortcut Router: A local DNS-style redirection tool.
This module provides a Flask web server that routes short, custom keywords
to full URLs stored in a local JSON file. It also includes a web dashboard
to manage these shortcuts.
"""

import json
import os

from flask import Flask, redirect, render_template, request

app = Flask(__name__)
DATA_FILE = "shortcuts.json"


def load_shortcuts():
    """
    Read the shortcuts from the local JSON database.

    :return: A dictionary of shortcuts where keys are keywords and values are URLs.
    :rtype: dict
    """
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_shortcuts(shortcuts):
    """
    Persist the provided dictionary of shortcuts to the JSON file.

    :param shortcuts: The dictionary containing keyword-to-URL mappings.
    :type shortcuts: dict
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(shortcuts, f, indent=4)


@app.route("/")
def index():
    """
    Render the administrative dashboard showing all existing shortcuts.

    :return: The rendered HTML template for the management UI.
    """
    shortcuts = load_shortcuts()
    return render_template("index.html", shortcuts=shortcuts)


@app.route("/add", methods=["POST"])
def add_shortcut():
    """
    Process form data to add a new shortcut to the system.

    Extracts 'key' and 'url' from the POST request, sanitizes them,
    and updates the JSON database before redirecting back to the index.
    """
    key = request.form.get("key").strip().lower()
    url = request.form.get("url").strip()

    if key and url:
        shortcuts = load_shortcuts()
        shortcuts[key] = url
        save_shortcuts(shortcuts)

    return redirect("/")


@app.route("/delete/<key>", methods=["POST"])
def delete_shortcut(key):
    """
    Remove a specific shortcut from the database based on its keyword.

    :param key: The keyword identifier to be deleted.
    :type key: str
    """
    shortcuts = load_shortcuts()
    if key in shortcuts:
        del shortcuts[key]
        save_shortcuts(shortcuts)
    return redirect("/")


@app.route("/<keyword>")
@app.route("/<keyword>/<path:rest>")
def router(keyword, rest=None):
    """
    The core redirection engine that maps keywords to their destinations.

    If a match is found, the user is redirected to the target URL.
    If extra path information is provided (the 'rest' parameter), it
    is intelligently appended to the base URL.

    :param keyword: The shortcut keyword entered in the browser.
    :param rest: Optional additional path or query parameters.
    :return: A redirect response to the target URL or a 404 error message.
    """
    shortcuts = load_shortcuts()
    if keyword in shortcuts:
        base_url = shortcuts[keyword]
        if rest:
            # Handle potential trailing slashes for clean appending
            separator = "" if base_url.endswith(("/", "=", "&")) else "/"
            return redirect(f"{base_url}{separator}{rest}")
        return redirect(base_url)

    return f"Shortcut '{keyword}' not found.", 404


if __name__ == "__main__":
    app.run(port=80, debug=True)
