"""
Shortcut Router: A local DNS-style redirection tool.
This module provides a Flask web server that routes short, custom keywords
to full URLs stored in a local JSON file. It also includes a web dashboard
to manage these shortcuts.
"""

import json
import os
import re
import secrets
from urllib.parse import urlparse

from flask import Flask, abort, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)
DATA_FILE = "shortcuts.json"
RESERVED_PATHS = {"add", "delete", "static", "admin"}


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


def is_valid_key(key):
    """
    Validates the format of a shortcut key.

    A key is considered valid if:
    - It is not empty and its length does not exceed 50 characters.
    - It is not a reserved path (e.g., 'add', 'delete', 'static', 'admin').
    - It consists only of lowercase letters, numbers, hyphens, and underscores.

    :param key: The shortcut key to validate.
    :type key: str
    :return: True if the key is valid, False otherwise.
    :rtype: bool
    """
    if not key or len(key) > 50:
        return False
    if key in RESERVED_PATHS:
        return False
    return bool(re.match(r"^[a-z0-9_-]+$", key))


def save_shortcuts(shortcuts):
    """
    Persist the provided dictionary of shortcuts to the JSON file.

    :param shortcuts: The dictionary containing keyword-to-URL mappings.
    :type shortcuts: dict
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(shortcuts, f, indent=4)


def is_valid_token(token) -> bool:
    """
    Validates if the provided CSRF token matches the one stored in the user's session.

    This function is crucial for protecting against Cross-Site Request Forgery (CSRF) attacks.

    :param token: The CSRF token received from the client.
    :type token: str
    :return: True if the token is valid and matches the session token, False otherwise.
    :rtype: bool
    """
    if not token or token != session.get("csrf_token"):
        return False
    return True


@app.route("/")
def index():
    """
    Render the administrative dashboard showing all existing shortcuts.

    :return: The rendered HTML template for the management UI.
    """
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    shortcuts = load_shortcuts()
    return render_template(
        "index.html", shortcuts=shortcuts, csrf_token=session["csrf_token"]
    )


@app.route("/add", methods=["POST"])
def add_shortcut():
    """
    Process form data to add a new shortcut to the system.

    Extracts 'key' and 'url' from the POST request, sanitizes them,
    and updates the JSON database before redirecting back to the index.

    Ensure URL uses a safe scheme and has a network location
    """
    if not is_valid_token(request.form.get("csrf_token")):
        abort(403)

    key = request.form.get("key", "").strip().lower()
    url = request.form.get("url", "").strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https", "ftp", "ftps") or not parsed.netloc:
        return (
            "Invalid URL. Only http(s) and ftp(s) URLs with a domain are allowed.",
            400,
        )

    if key and url:
        shortcuts = load_shortcuts()
        shortcuts[key] = url
        save_shortcuts(shortcuts)

    return redirect("/")


@app.route("/delete/<key>", methods=["POST"])
def delete_shortcut(key):
    """
    Remove a specific shortcut from the database based on its keyword.

    This function also validates the CSRF token to ensure the request is legitimate.

    :param key: The keyword identifier to be deleted.
    :type key: str
    """
    if not is_valid_token(request.form.get("csrf_token")):
        abort(403)

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
            # Check if the base URL acts as a query prefix
            if "?" in base_url:
                # Safely append the parameter directly
                target_url = f"{base_url}{rest}"
            else:
                # Safely join paths, stripping excess slashes to prevent `site.com//path`
                target_url = f"{base_url.rstrip('/')}/{rest.lstrip('/')}"
            return redirect(target_url)

        return redirect(base_url)

    return f"Shortcut '{keyword}' not found.", 404


if __name__ == "__main__":
    app.run(port=80, debug=False)
