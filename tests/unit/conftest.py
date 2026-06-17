"""Shared test fixtures for stevefulme1.coreweave collection."""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


@pytest.fixture
def mock_module():
    """Create a mock AnsibleModule with K8s auth params."""
    module = MagicMock()
    module.params = {
        "state": "present",
        "kubeconfig": "/tmp/kube",
        "context": None,
        "namespace": "default",
    }
    module.check_mode = False
    module.fail_json = MagicMock(side_effect=SystemExit(1))
    module.exit_json = MagicMock(side_effect=SystemExit(0))
    return module


@pytest.fixture
def mock_module_check_mode(mock_module):
    """Create a mock AnsibleModule in check mode."""
    mock_module.check_mode = True
    return mock_module


@pytest.fixture
def mock_rest_module():
    """Create a mock AnsibleModule with REST API auth params."""
    module = MagicMock()
    module.params = {
        "state": "present",
        "api_token": "test-token",
        "api_url": "https://api.coreweave.com",
        "validate_certs": True,
        "timeout": 60,
    }
    module.check_mode = False
    module.fail_json = MagicMock(side_effect=SystemExit(1))
    module.exit_json = MagicMock(side_effect=SystemExit(0))
    return module


@pytest.fixture
def mock_rest_module_check_mode(mock_rest_module):
    """Create a mock REST module in check mode."""
    mock_rest_module.check_mode = True
    return mock_rest_module
