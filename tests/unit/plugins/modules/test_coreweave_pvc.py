"""Unit tests for coreweave_pvc module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_pvc"

PVC_PARAMS = {
    "kubeconfig": "/tmp/kube",  # noqa: S108
    "context": None,
    "namespace": "default",
    "state": "present",
    "name": "test-pvc",
    "storage_size": "10Gi",
    "access_modes": ["ReadWriteOnce"],
    "volume_mode": "Filesystem",
    "storage_class_name": None,
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
        mock_module = _make_module({**PVC_PARAMS})
        mock_ansible_cls.return_value = mock_module
        mock_apply.return_value = {"changed": True, "result": {"metadata": {"name": "test-pvc"}}}

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_pvc import main
        with pytest.raises(SystemExit):
            main()

        mock_module.exit_json.assert_called_once()
        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestDelete:
    @patch(f"{MODULE_PATH}.apply_resource")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_delete(self, mock_ansible_cls, mock_apply):
        mock_module = _make_module({**PVC_PARAMS, "state": "absent"})
        mock_ansible_cls.return_value = mock_module
        mock_apply.return_value = {"changed": True, "result": {}}

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_pvc import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestBuildManifest:
    def test_pvc_manifest(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_pvc import build_manifest
        manifest = build_manifest(PVC_PARAMS)
        assert manifest["kind"] == "PersistentVolumeClaim"
        assert manifest["spec"]["resources"]["requests"]["storage"] == "10Gi"
        assert manifest["spec"]["accessModes"] == ["ReadWriteOnce"]
