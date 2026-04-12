import argparse
import json

from flask import Flask, redirect

app = Flask(__name__)
DATA_FILE = "shortcuts.json"


def main():
    # 1. Handle CLI arguments for managing shortcuts
    parser = argparse.ArgumentParser(description="Manage your 'to/' shortcuts.")
    parser.add_argument(
        "--add", nargs=2, metavar=("key", "url"), help="Add a new shortcut"
    )
    parser.add_argument(
        "--list", action="store_true", help="List all current shortcuts"
    )
    parser.add_argument("--run", action="store_true", help="Run the redirect server")

    args = parser.parse_args()

    if args.add:
        add_shortcut(args.add[0], args.add[1])
    elif args.list:
        list_shortcuts()
    elif args.run:
        print("Server starting on http://127.0.0.1:8080")
        app.run(port=80)
    else:
        parser.print_help()


def load_shortcuts():
    """Load shortcuts from the JSON file."""
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_shortcuts(shortcuts):
    """Save shortcuts to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(shortcuts, f, indent=4)


def add_shortcut(key, url):
    """Business logic to add a new shortcut."""
    shortcuts = load_shortcuts()
    shortcuts[key] = url
    save_shortcuts(shortcuts)
    print(f"Added shortcut: {key} -> {url}")


def list_shortcuts():
    """Print all shortcuts in a clean format."""
    shortcuts = load_shortcuts()
    if not shortcuts:
        print("No shortcuts found.")
        return
    print("\nYour Current Shortcuts:")
    for key, url in shortcuts.items():
        print(f"  {key:10} -> {url}")


# --- Flask Routes ---


@app.route("/<keyword>")
@app.route("/<keyword>/<path:rest>")
def router(keyword, rest=None):
    shortcuts = load_shortcuts()
    if keyword in shortcuts:
        base_url = shortcuts[keyword]
        # Append extra path if using dynamic parameters (e.g. to/wiki/Python)
        if rest:
            return redirect(f"{base_url}{rest}")
        return redirect(base_url)

    return f"Shortcut '{keyword}' not found in {DATA_FILE}.", 404


if __name__ == "__main__":
    main()
