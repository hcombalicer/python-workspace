"""Pytest coverage for the GCP billing automation Cloud Function module."""

import base64
import importlib.util
import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock


def _install_dependency_stubs(monkeypatch):
    """Register minimal stub modules so `main.py` can be imported in tests."""
    functions_framework = types.ModuleType("functions_framework")
    functions_framework.cloud_event = lambda func: func

    cloudevents = types.ModuleType("cloudevents")
    cloudevents_http = types.ModuleType("cloudevents.http")
    cloudevents_event = types.ModuleType("cloudevents.http.event")
    cloudevents_event.CloudEvent = object

    google = types.ModuleType("google")
    api_core = types.ModuleType("google.api_core")
    exceptions = types.ModuleType("google.api_core.exceptions")

    class PermissionDeniedError(Exception):
        pass

    class GoogleAPICallError(Exception):
        pass

    exceptions.PermissionDenied = PermissionDeniedError
    exceptions.GoogleAPICallError = GoogleAPICallError
    api_core.exceptions = exceptions

    cloud = types.ModuleType("google.cloud")
    billing_v1 = types.ModuleType("google.cloud.billing_v1")

    class CloudBillingClient:
        pass

    class ProjectBillingInfo:
        def __init__(self, billing_account_name=""):
            self.billing_account_name = billing_account_name

    billing_v1.CloudBillingClient = CloudBillingClient
    billing_v1.ProjectBillingInfo = ProjectBillingInfo

    logging = types.ModuleType("google.cloud.logging")
    logging.Client = MagicMock()

    cloud.billing_v1 = billing_v1
    cloud.logging = logging

    modules = {
        "functions_framework": functions_framework,
        "cloudevents": cloudevents,
        "cloudevents.http": cloudevents_http,
        "cloudevents.http.event": cloudevents_event,
        "google": google,
        "google.api_core": api_core,
        "google.api_core.exceptions": exceptions,
        "google.cloud": cloud,
        "google.cloud.billing_v1": billing_v1,
        "google.cloud.logging": logging,
    }

    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)


def _load_main(monkeypatch):
    """Import `main.py` into an isolated test module with stubbed dependencies."""
    _install_dependency_stubs(monkeypatch)
    module_name = "gcp_billing_automation_main_under_test"
    sys.modules.pop(module_name, None)

    spec = importlib.util.spec_from_file_location(
        module_name, Path(__file__).with_name("main.py")
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _cloud_event(cost_amount, budget_amount):
    """Build a minimal CloudEvent-like object for budget alert test cases."""
    payload = {"costAmount": cost_amount, "budgetAmount": budget_amount}
    encoded_payload = base64.b64encode(json.dumps(payload).encode()).decode()
    return SimpleNamespace(data={"message": {"data": encoded_payload}})


def test_get_project_id_returns_environment_value(monkeypatch):
    """Return the environment project ID without calling the metadata server."""
    main = _load_main(monkeypatch)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    mock_urlopen = MagicMock()
    monkeypatch.setattr(main.urllib.request, "urlopen", mock_urlopen)

    assert main.get_project_id() == "test-project"
    mock_urlopen.assert_not_called()


def test_stop_billing_takes_no_action_when_cost_is_within_budget(monkeypatch, capsys):
    """Skip billing checks and disable calls when the budget is not exceeded."""
    main = _load_main(monkeypatch)
    monkeypatch.setattr(main, "get_project_id", MagicMock(return_value="test-project"))
    is_billing_enabled = MagicMock()
    disable_billing = MagicMock()
    monkeypatch.setattr(main, "_is_billing_enabled", is_billing_enabled)
    monkeypatch.setattr(main, "_disable_billing_for_project", disable_billing)

    main.stop_billing(_cloud_event(cost_amount=90.02, budget_amount=100.00))

    is_billing_enabled.assert_not_called()
    disable_billing.assert_not_called()
    assert "No action required" in capsys.readouterr().out


def test_stop_billing_disables_billing_when_budget_is_exceeded(monkeypatch):
    """Disable billing when the incoming budget alert reports an overage."""
    main = _load_main(monkeypatch)
    monkeypatch.setattr(main, "get_project_id", MagicMock(return_value="test-project"))
    is_billing_enabled = MagicMock(return_value=True)
    disable_billing = MagicMock()
    monkeypatch.setattr(main, "_is_billing_enabled", is_billing_enabled)
    monkeypatch.setattr(main, "_disable_billing_for_project", disable_billing)

    main.stop_billing(_cloud_event(cost_amount=405.50, budget_amount=100.00))

    is_billing_enabled.assert_called_once_with("projects/test-project")
    disable_billing.assert_called_once_with("projects/test-project", False)


def test_stop_billing_skips_disable_when_billing_is_already_disabled(monkeypatch):
    """Avoid the disable call when project billing is already turned off."""
    main = _load_main(monkeypatch)
    monkeypatch.setattr(main, "get_project_id", MagicMock(return_value="test-project"))
    monkeypatch.setattr(main, "_is_billing_enabled", MagicMock(return_value=False))
    disable_billing = MagicMock()
    monkeypatch.setattr(main, "_disable_billing_for_project", disable_billing)

    main.stop_billing(_cloud_event(cost_amount=405.50, budget_amount=100.00))

    disable_billing.assert_not_called()


def test_is_billing_enabled_returns_api_response(monkeypatch):
    """Return the billing-enabled flag provided by the billing API client."""
    main = _load_main(monkeypatch)
    main.billing_client = MagicMock()
    main.billing_client.get_project_billing_info.return_value = SimpleNamespace(
        billing_enabled=True
    )

    assert main._is_billing_enabled("projects/test-project") is True
    main.billing_client.get_project_billing_info.assert_called_once_with(
        name="projects/test-project"
    )


def test_is_billing_enabled_assumes_enabled_when_api_call_fails(monkeypatch):
    """Fall back to `True` when billing status cannot be retrieved."""
    main = _load_main(monkeypatch)
    main.billing_client = MagicMock()
    main.billing_client.get_project_billing_info.side_effect = RuntimeError("api error")

    assert main._is_billing_enabled("projects/test-project") is True


def test_disable_billing_for_project_unlinks_billing_account(monkeypatch):
    """Send an update request with an empty billing account and log the action."""
    main = _load_main(monkeypatch)
    main.billing_client = MagicMock()
    main.billing_client.update_project_billing_info.return_value = "updated"
    logger = MagicMock()
    logging_client = MagicMock()
    logging_client.logger.return_value = logger
    monkeypatch.setattr(main.logging, "Client", MagicMock(return_value=logging_client))

    main._disable_billing_for_project("projects/test-project", False)

    main.billing_client.update_project_billing_info.assert_called_once()
    _, kwargs = main.billing_client.update_project_billing_info.call_args
    assert kwargs["name"] == "projects/test-project"
    assert kwargs["project_billing_info"].billing_account_name == ""
    logger.log_text.assert_called_once_with(
        "Billing disabled: updated", severity="CRITICAL"
    )
