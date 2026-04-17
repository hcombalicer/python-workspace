"""
Exchange Rate Monitor and Alerter

This script automates the monitoring of the USD to PHP exchange rate using
fxratesapi.com API. It compares the current rate
against a user-defined threshold and sends a notification via Telegram
if the condition is met.

Usage:
    # Run tests
    python automation/exchange_rate/exchange_rate.py test

    # Run the monitor with a custom threshold
    python automation/exchange_rate/exchange_rate.py --threshold 58.0

Environment Variables:
    FXRATESAPI_KEY: Your fxratesapi.com API token.
    TELEGRAM_TOKEN: Your Telegram Bot API token from @BotFather.
    TELEGRAM_CHAT_ID: Your unique Telegram chat ID.
"""

import argparse
import os
import sys
import unittest
from typing import Optional

import requests
import telebot


def get_exchange_rate() -> Optional[float]:
    """
    Fetches the current USD to PHP exchange rate using fxratesapi.com.

    Retrieves the API key from the FXRATESAPI_KEY environment variable.

    Returns:
        float: The current exchange rate as a number (e.g., 58.12).
        None: If the API call fails or the response is non-numeric.
    """
    try:
        api_key = os.environ.get("FXRATESAPI_KEY")
        if not api_key:
            print("Error: FXRATESAPI_KEY environment variable not set.")
            return None

        headers = {"Authorization": api_key}
        url = "https://api.fxratesapi.com/latest"
        params = {
            "base": "USD",
            "currencies": "PHP",
            "resolution": "1m",
            "amount": "1",
            "places": "6",
            "format": "json",
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        rate = data["rates"]["PHP"]
        return float(rate)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching rate from API: {e}")
        return None
    except KeyError:
        print("Error: Could not parse exchange rate from API response.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def check_and_notify(current: float, threshold: float) -> bool:
    """
    Determines if the current rate meets the alert criteria.

    Args:
        current_rate (float): The live rate retrieved from the API.
        threshold (float): The maximum rate allowed before triggering an alert.

    Returns:
        bool: True if the current_rate is less than or equal to the threshold,
              False otherwise.
    """
    if current is None:
        return False
    return current <= threshold


def send_notification(rate: float) -> None:
    """
    Dispatches a notification message via the Telegram Bot API.

    Args:
        rate (float): The exchange rate value to include in the alert message.

    Raises:
        telebot.apihelper.ApiException: If there is an issue with the Telegram
                                       token or network.
    """
    bot = telebot.TeleBot(os.environ["TELEGRAM_TOKEN"])
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    bot.send_message(
        chat_id,
        f"🚨 USD/PHP Alert: The rate is currently {rate}, which is below your threshold!",
    )


# --- UNIT TESTS ---
class TestRateLogic(unittest.TestCase):
    """
    Unit tests for the core logic of the exchange rate monitor.
    """

    def test_threshold_logic(self) -> None:
        """
        Testing the binary to some numbers
        """
        self.assertTrue(check_and_notify(57.9, 58.0))
        self.assertFalse(check_and_notify(58.1, 58.0))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Remove 'test' from argv so unittest doesn't get confused
        sys.argv.pop(1)
        unittest.main()
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--threshold", type=float, default=58.0)
        args = parser.parse_args()

        current_rate = get_exchange_rate()
        if current_rate is None:
            print("Skipping check: Could not retrieve current exchange rate.")
            sys.exit(0)  # Exit gracefully
        print(f"Rate: {current_rate} | Target: {args.threshold}")

        if check_and_notify(current_rate, args.threshold):
            send_notification(current_rate)
            print("Alert triggered.")
