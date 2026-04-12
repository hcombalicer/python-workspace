"""
Test suite for the Shortcut Manager Flask application.

This module contains unit tests and integration tests using pytest.
It utilizes pytest fixtures to create a temporary, isolated environment
to ensure that the actual 'shortcuts.json' file is never overwritten
or modified during testing.
"""

import pytest
from project import app, load_shortcuts, save_shortcuts

# --- FIXTURES ---


@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Provide a simulated web client and a temporary JSON file for safe testing.

    This fixture creates a temporary directory using `tmp_path` and points
    the application's DATA_FILE constant to a fake JSON file using `monkeypatch`.
    It then yields a Flask test client to simulate HTTP requests.
    """
    test_file = tmp_path / "test_shortcuts.json"
    monkeypatch.setattr("project.DATA_FILE", str(test_file))

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# --- TESTS FOR HELPER FUNCTIONS ---


def test_load_shortcuts_empty(client):
    """
    Test loading shortcuts when the JSON file does not exist.

    Expectation: The function should gracefully handle the missing file
    and return an empty dictionary.
    """
    assert load_shortcuts() == {}


def test_save_and_load_shortcuts(client):
    """
    Test the fundamental File I/O operations.

    Expectation: Data saved via `save_shortcuts` should be exactly
    the same when retrieved via `load_shortcuts`.
    """
    test_data = {"test": "https://example.com"}
    save_shortcuts(test_data)

    loaded_data = load_shortcuts()
    assert loaded_data == test_data
    assert "test" in loaded_data


# --- TESTS FOR FLASK ROUTES ---


def test_index_route(client):
    """
    Test the root/dashboard endpoint.

    Expectation: A GET request to '/' should return a 200 OK status
    and contain the expected HTML title text.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Shortcut Dashboard" in response.data


def test_add_shortcut_route(client):
    """
    Test the web form submission for adding a new shortcut.

    Expectation: A POST request to '/add' should return a 302 Redirect
    and successfully write the new key-value pair to the JSON file.
    """
    response = client.post(
        "/add", data={"key": "cs50", "url": "https://cs50.harvard.edu"}
    )

    assert response.status_code == 302

    data = load_shortcuts()
    assert data["cs50"] == "https://cs50.harvard.edu"


def test_router_redirect(client):
    """
    Test the core URL redirection logic.

    Expectation: Visiting a valid shortcut path should return a 302 Redirect
    to the correct destination URL specified in the HTTP headers.
    """
    save_shortcuts({"gh": "https://github.com"})

    response = client.get("/gh")

    assert response.status_code == 302
    assert response.headers["Location"] == "https://github.com"


def test_router_dynamic_redirect(client):
    """
    Test the dynamic parameter appendage feature.

    Expectation: If a user types additional path parameters after the shortcut
    (e.g., 'google/python'), the extra string should be cleanly appended
    to the base URL.
    """
    save_shortcuts({"google": "https://google.com/search?q="})

    response = client.get("/google/pytest")

    assert response.status_code == 302
    assert response.headers["Location"] == "https://google.com/search?q=pytest"


def test_delete_shortcut_route(client):
    """
    Test the removal of a shortcut via the web interface.

    Expectation: A POST request to '/delete/<key>' should return a 302 Redirect
    and completely remove the target key from the JSON file.
    """
    save_shortcuts({"removeme": "https://badwebsite.com"})

    response = client.post("/delete/removeme")

    assert response.status_code == 302

    data = load_shortcuts()
    assert "removeme" not in data
