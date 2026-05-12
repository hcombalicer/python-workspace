"""
This module contains a Cloud Function that automatically disables Google Cloud
Platform (GCP) billing for the project where it is deployed, when budget
thresholds are exceeded.

The function `stop_billing` is triggered by a Cloud Event (typically from a
Pub/Sub message sent by GCP Billing Budget alerts). It decodes the budget
alert data to check if cost thresholds (actual or forecasted) are met or
exceeded.

If the budget is exceeded, it then uses `get_project_id()` to identify
the current project. It proceeds to disable billing for this specific project
by unlinking it from its billing account. This is a critical action designed
to prevent further unauthorized spending in the project where this function
is hosted.

Error handling is included to catch permission issues and general API call
errors during the billing deactivation process.
"""

import base64
import json
import os
import urllib.request

import functions_framework
from cloudevents.http.event import CloudEvent
from google.api_core import exceptions
from google.cloud import billing_v1, logging

billing_client = billing_v1.CloudBillingClient()


def get_project_id() -> str:
    """Retrieves the Google Cloud Project ID.

    This function first attempts to get the project ID from the
    `GOOGLE_CLOUD_PROJECT` environment variable. If the environment
    variable is not set or is None, it then attempts to retrieve the
    project ID from the Google Cloud metadata server.

    Returns:
        str: The Google Cloud Project ID.

    Raises:
        ValueError: If the project ID cannot be determined either from
                    the environment variable or the metadata server.
    """

    # Read the environment variable, usually set manually
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project_id is not None:
        return project_id

    # Otherwise, get the `project-id`` from the Metadata server
    url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
    req = urllib.request.Request(url)
    req.add_header("Metadata-Flavor", "Google")
    project_id = urllib.request.urlopen(req).read().decode()

    if project_id is None:
        raise ValueError("project-id metadata not found.")

    return project_id


@functions_framework.cloud_event
def stop_billing(cloud_event: CloudEvent) -> None:
    """
    Handles Cloud Events triggered by GCP Billing Budget alerts.

    This function processes incoming Cloud Events, typically from a Pub/Sub
    message. It extracts the budget alert data (cost amount, budget amount)
    from the message payload.

    If the `cost_amount` exceeds the `budget_amount`, the function proceeds
    to get the Project ID of the current environment where the Cloud Function
    is running using `get_project_id()`. It then calls the
    `_is_billing_enabled` and `_disable_billing_for_project` helper functions
    to check and disable billing for that specific project. This ensures that
    billing is disabled only for the project that triggered the alert.

    Args:
        cloud_event (CloudEvent): The incoming Cloud Event object containing
                                  the Pub/Sub message from a billing alert.
    """

    simulate_deactivation = False

    project_id = get_project_id()
    project_name = f"projects/{project_id}"

    event_data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")

    event_dict = json.loads(event_data)
    cost_amount = event_dict["costAmount"]
    budget_amount = event_dict["budgetAmount"]
    print(f"Cost: {cost_amount} Budget: {budget_amount}")

    if cost_amount <= budget_amount:
        print("No action required. Current cost is within budget.")
        return

    print(f"Budget exceeded. Disabling billing for project '{project_name}'...")

    if _is_billing_enabled(project_name):
        _disable_billing_for_project(project_name, simulate_deactivation)
    else:
        print(f"Billing is already disabled for project '{project_name}'.")


def _is_billing_enabled(project_name: str) -> bool:
    """Determine whether billing is enabled for a project.

    Args:
        project_name: The resource name of the project to check (e.g., "projects/project-id-123").

    Returns:
        bool: True if billing is enabled for the project, False otherwise.

    Raises:
        google.api_core.exceptions.GoogleAPICallError: If there is an issue
            communicating with the Google Cloud Billing API, or if the API
            call returns an error.
    """
    try:
        print(f"Getting billing info for project '{project_name}'...")
        response = billing_client.get_project_billing_info(name=project_name)

        return response.billing_enabled
    except Exception as e:
        print(f"Error getting billing info: {e}")
        print(
            "Unable to determine if billing is enabled on specified project, "
            "assuming billing is enabled."
        )

        return True


def _disable_billing_for_project(
    project_name: str,
    simulate_deactivation: bool,
) -> None:
    """Disable billing for a project by removing its billing account.

    Args:
        project_name: The resource name of the project for which to disable billing
        (e.g., "projects/project-id-123"). simulate_deactivation:
            If True, the function will not actually disable billing but will
            log the action as simulated. Useful for validation with test budgets.

    Raises:
        google.api_core.exceptions.PermissionDenied: If the service account
            does not have the necessary permissions to update the project's
            billing information.
        google.api_core.exceptions.GoogleAPICallError: If there is an issue
            communicating with the Google Cloud Billing API, or if the API
            call returns an error.
    """

    # Log this operation in Cloud Logging
    logging_client = logging.Client()
    logger = logging_client.logger(name="disable-billing")

    if simulate_deactivation:
        entry_text = "Billing disabled. (Simulated)"
        print(entry_text)
        logger.log_text(entry_text, severity="CRITICAL")
        return

    try:
        # To disable billing set the `billing_account_name` field to empty
        project_billing_info = billing_v1.ProjectBillingInfo(billing_account_name="")

        response = billing_client.update_project_billing_info(
            name=project_name, project_billing_info=project_billing_info
        )

        entry_text = f"Billing disabled: {response}"
        print(entry_text)
        logger.log_text(entry_text, severity="CRITICAL")
    except (exceptions.PermissionDenied, exceptions.GoogleAPICallError) as e:
        print(f"Failed to disable billing for project '{project_name}': {e}")
