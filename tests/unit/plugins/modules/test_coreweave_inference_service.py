"""Unit tests for coreweave_inference_service module."""

from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type


from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_inference_service"

ISVC_PARAMS = {
    "kubeconfig": "/tmp/kube",  # noqa: S108
    "context": None,
    "namespace": "default",
    "state": "present",
    "name": "test-isvc",
    "runtime": "custom",
    "container_image": "test:latest",
    "container_command": None,
    "container_args": None,
    "container_env": None,
    "container_port": 80,
    "storage_uri": None,
    "gpu_type": "Quadro_RTX_5000",
    "gpu_count": 1,
    "cpu_request": None,
    "cpu_limit": None,
    "memory_request": None,
    "memory_limit": None,
    "min_replicas": 1,
    "max_replicas": 1,
    "container_concurrency": None,
    "region": None,
    "labels": {},
    "annotations": {},
}


def _make_module(params):
    module = MagicMock()
    module.params = params
    module.check_mode = False
    module.fail_json = MagicMock(side_effect=SystemExit(1))
    module.exit_json = MagicMock(side_effect=SystemExit(0))
    return module


class TestCreate:
    @patch(f"{MODULE_PATH}.apply_resource")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_create(self, mock_ansible_cls, mock_apply):
        mock_module = _make_module({**ISVC_PARAMS})
        mock_ansible_cls.return_value = mock_module
        mock_apply.return_value = {"changed": True, "result": {"metadata": {"name": "test-isvc"}}}

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_inference_service import main
        with pytest.raises(SystemExit):
            main()

        mock_module.exit_json.assert_called_once()
        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestDelete:
    @patch(f"{MODULE_PATH}.apply_resource")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_delete(self, mock_ansible_cls, mock_apply):
        mock_module = _make_module({**ISVC_PARAMS, "state": "absent", "container_image": None, "gpu_type": None})
        mock_ansible_cls.return_value = mock_module
        mock_apply.return_value = {"changed": True, "result": {}}

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_inference_service import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True
