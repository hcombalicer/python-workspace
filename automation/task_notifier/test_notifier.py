"""
Unit Tests for Task Notifier
---------------------------
Mocks Google Tasks API responses and Telegram API calls to verify that
the overdue logic and messaging flow work correctly without external hits.
"""

import unittest
from unittest.mock import MagicMock, patch

from notifier import check_and_notify


class TestTaskNotifier(unittest.TestCase):
    """
    Test suite for the notifier script using unittest and mock patches.
    """

    @patch("notifier.get_tasks_service")
    @patch("notifier.send_telegram_message")
    @patch.dict(
        "os.environ", {"TELEGRAM_BOT_TOKEN": "fake_bot", "TELEGRAM_CHAT_ID": "123"}
    )
    def test_overdue_logic(self, mock_send, mock_service):
        """
        Tests the check_and_notify function to ensure it correctly identifies
        overdue tasks and triggers the Telegram message function.

        Args:
            mock_send (MagicMock): Mocked version of the send_telegram_message function.
            mock_service (MagicMock): Mocked version of the get_tasks_service function.
        """
        # Set up the mock service to return a specific 'Important' list
        mock_tasks_api = MagicMock()
        mock_service.return_value = mock_tasks_api

        mock_tasks_api.tasklists.return_value.list.return_value.execute.return_value = {
            "items": [{"id": "list_123", "title": "Important"}]
        }

        # Set up the mock service to return one overdue task (dated in the past)
        mock_tasks_api.tasks.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "title": "Test Overdue Task",
                    "due": "2000-01-01T00:00:00Z",  # Definitely overdue
                }
            ]
        }

        # Run the logic
        check_and_notify()

        # Assertions
        self.assertTrue(
            mock_send.called,
            "Telegram message should have been sent for an overdue task.",
        )
        sent_message = mock_send.call_args[0][2]
        self.assertIn(
            "Test Overdue Task",
            sent_message,
            "The task title should be in the message.",
        )
        self.assertIn(
            "1/1", sent_message, "The message should include the correct task count."
        )


if __name__ == "__main__":
    unittest.main()
