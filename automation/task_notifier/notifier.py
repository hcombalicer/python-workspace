"""
Google Tasks Overdue Notifier
----------------------------
A script to fetch overdue tasks from a specific Google Task list ('Important')
and send reminders via a Telegram Bot. Designed to run as a GitHub Action.
"""

import os
import time
from datetime import datetime, timezone

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_tasks_service():
    """
    Authenticates with Google using the token.json file and initializes
    the Google Tasks API service. Handles automatic token refreshment.

    Returns:
        googleapiclient.discovery.Resource: An authorized Google Tasks service object.

    Raises:
        FileNotFoundError: If the token.json file is missing.
    """
    token_path = "token.json"
    if not os.path.exists(token_path):
        raise FileNotFoundError(
            "token.json not found. Ensure GitHub Secret is configured."
        )

    creds = Credentials.from_authorized_user_file(token_path)
    # Refresh the access token using the refresh_token if it has expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("tasks", "v1", credentials=creds)


def send_telegram_message(bot_token, chat_id, text):
    """
    Sends a POST request to the Telegram Bot API to deliver a message.

    Args:
        bot_token (str): The unique API token for the Telegram bot.
        chat_id (str): The unique identifier for the target chat or user.
        text (str): The message content formatted in Markdown.

    Returns:
        None
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


def check_and_notify():
    """
    The main execution logic:
    1. Loads environment variables for Telegram.
    2. Connects to Google Tasks.
    3. Finds the task list named 'Important'.
    4. Filters for tasks that are past their due date.
    5. Sends an individual Telegram alert for each overdue task.

    Returns:
        None
    """
    bot_token_value = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    target_list_name = "Important"

    if not bot_token_value or not chat_id:
        print("Error: Telegram credentials missing in Environment Variables.")
        return

    service = get_tasks_service()

    # Fetch all task lists for the user
    results = service.tasklists().list().execute()
    items = results.get("items", [])
    important_list = next(
        (item for item in items if item["title"] == target_list_name), None
    )

    if not important_list:
        print(f"List '{target_list_name}' not found.")
        return

    # Fetch tasks from the specific list (excluding completed/hidden tasks)
    tasks_results = (
        service.tasks()
        .list(tasklist=important_list["id"], showCompleted=False, showHidden=False)
        .execute()
    )

    all_tasks = tasks_results.get("items", [])
    now = datetime.now(timezone.utc)

    # Identify tasks where the current time is greater than the due date
    overdue_tasks = []
    for task in all_tasks:
        if "due" in task:
            due_date = datetime.fromisoformat(task["due"].replace("Z", "+00:00"))
            if now > due_date:
                overdue_tasks.append(task)

    total_overdue = len(overdue_tasks)

    if total_overdue > 0:
        for index, task in enumerate(overdue_tasks):
            due_str = datetime.fromisoformat(
                task["due"].replace("Z", "+00:00")
            ).strftime("%Y-%m-%d")

            message = (
                f"🚨 *OVERDUE ALERT [{index + 1}/{total_overdue}]* 🚨\n\n"
                f"Task: *{task['title']}*\n"
                f"Due Date: {due_str}\n\n"
                f"💡 *Note:* Perform this task **immediately**."
            )

            send_telegram_message(bot_token_value, chat_id, message)
            time.sleep(1)  # Delay to respect Telegram's rate limits


if __name__ == "__main__":
    check_and_notify()
