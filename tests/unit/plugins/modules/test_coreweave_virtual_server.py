"""Unit tests for coreweave_virtual_server module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_virtual_server"

VS_PARAMS = {
    "kubeconfig": "/tmp/kube",  # noqa: S108
    "context": None,
    "namespace": "default",
    "state": "present",
    "name": "test-vs",
    "region": "ORD1",
    "os_type": "linux",
    "gpu_type": "Quadro_RTX_4000",
    "gpu_count": 1,
    "cpu_count": 4,
    "memory": "16Gi",
    "root_disk_size": "40Gi",
    "storage_class_name": None,
    "root_disk_source": None,
    "users": None,
    "network_public": True,
    "tcp_ports": [22],
    "udp_ports": None,
    "cloud_init": None,
    "initialize_running": True,
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
        mock_module = _make_module({**VS_PARAMS})
        mock_ansible_cls.return_value = mock_module
        mock_apply.return_value = {"changed": True, "result": {"metadata": {"name": "test-vs"}}}

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_virtual_server import main
        with pytest.raises(SystemExit):
            main()

        mock_module.exit_json.assert_called_once()
        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestDelete:
    @patch(f"{MODULE_PATH}.apply_resource")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_delete(self, mock_ansible_cls, mock_apply):
        mock_module = _make_module({**VS_PARAMS, "state": "absent", "gpu_type": None})
        mock_ansible_cls.return_value = mock_module
        mock_apply.return_value = {"changed": True, "result": {}}

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_virtual_server import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestBuildManifest:
    def test_manifest_has_gpu(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_virtual_server import build_manifest
        manifest = build_manifest(VS_PARAMS)
        assert manifest["kind"] == "VirtualServer"
        assert manifest["spec"]["resources"]["gpu"]["type"] == "Quadro_RTX_4000"

    def test_manifest_no_gpu(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_virtual_server import build_manifest
        manifest = build_manifest({**VS_PARAMS, "gpu_type": None})
        assert "gpu" not in manifest["spec"]["resources"]
