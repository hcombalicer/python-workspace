# Shortcut Router

## [Video Demo](https://youtu.be/vhpELrOA6fc)

## Description

The **Shortcut Router** is a powerful local URL redirection tool designed to streamline
your workflow. It allows you to create custom, memorable keywords (e.g., `my-budget-tracker`)
that instantly redirect to long, complex URLs (e.g., `https://docs.google.com/spreadsheets/d/123xyz`).
This means you can ditch bookmarks and quickly access frequently used resources directly from your browser's
address bar by typing something like `to/my-budget-tracker`.

Built with Flask, the project includes an intuitive web dashboard for effortless management of your
shortcuts – adding new ones, viewing existing entries, and removing outdated rules is simple and
straightforward. Integrated security measures, such as CSRF protection, ensure your custom redirects remain secure.

---

## Getting Started: Effortless Setup

To get your Shortcut Router up and running in minutes, follow these simple steps:

1. **Configure Your Local Hosts File**:
    The Shortcut Router operates using a special local domain, `to`, which must point to your computer's localhost. This is a one-time setup. Execute the provided bash script to automatically add the necessary entry to your `/etc/hosts` file:

    ```bash
    chmod +x add_hosts_entry.sh
    sudo ./add_hosts_entry.sh
    ```

    You will be prompted for your administrator password to modify `/etc/hosts`, a system-protected file.

2. **Install Python Dependencies**:
    Navigate to the project directory in your terminal. Install all required Python libraries using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**:
    Launch the Flask web application. The Shortcut Router is configured to run on **port 80** for seamless browser integration (no need to type port numbers).

    ```bash
    python project.py
    ```

    **Note:** Since port 80 is a privileged port on most operating systems, you might need to run the application with `sudo`:

    ```bash
    sudo python project.py
    ```

4. **Access the Dashboard & Use Your Shortcuts**:
    Once the application is running, open your web browser and navigate directly to `http://to/`. Here, you'll find your shortcut management dashboard. Add your first shortcut, and then simply type `to/YOUR_KEYWORD` (e.g., `to/my-budget-tracker`) into your browser's address bar to experience instant redirection!

---

### Project Files: A Quick Look

* **`project.py`**: The heart of the application, managing all web routes, shortcut logic (loading, saving), and Flask server operations.
* **`test_project.py`**: A comprehensive suite of `pytest` unit and integration tests to ensure the application's reliability.
* **`shortcuts.json`**: This file stores all your custom keyword-to-URL mappings persistently.
* **`templates/index.html`**: The HTML template for the user-friendly web dashboard where you manage your shortcuts.
* **`requirements.txt`**: Lists all external Python libraries the project depends on (e.g., Flask).
* **`add_hosts_entry.sh`**: A utility script to configure your system's `/etc/hosts` file, essential for the `to/` domain to work.

---

### Design Decisions: Why It Works This Way

* **Flask Microframework**: Chosen for its lightweight nature and flexibility, allowing for a focused and efficient application without unnecessary overhead.
* **JSON for Data Storage**: A simple `shortcuts.json` file was used for ease of setup and local persistence, avoiding the complexity of a full database for this project's scope.
* **CSRF Protection**: Implemented for all critical actions (like adding or deleting shortcuts) to safeguard against Cross-Site Request Forgery attacks, enhancing security.
* **Robust URL Validation**: Ensures that only safely formatted URLs are added, preventing potential security vulnerabilities or broken redirects.
* **Dynamic Path Handling**: Allows for more powerful shortcuts where additional path segments can be intelligently appended to the target URL (e.g., `to/google/search-query`).
* **Reserved Keywords**: Prevents conflicts by designating specific words (like `add`, `delete`) as internal system commands, ensuring smooth operation.
* **Port 80 for Simplicity**: Running on the default HTTP port (80) means you don't have to type `:8000` or `:5000` after `to/` in your browser, offering a cleaner and more intuitive user experience.
