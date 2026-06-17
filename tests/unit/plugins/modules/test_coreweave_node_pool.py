"""Unit tests for coreweave_node_pool module."""

from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool"

NP_PARAMS = {
    "kubeconfig": "/tmp/kube",  # noqa: S108
    "context": None,
    "namespace": "default",
    "state": "present",
    "name": "test-pool",
    "instance_type": "gd-8xa100-i128",
    "target_nodes": 4,
    "target_racks": None,
    "min_nodes": 2,
    "max_nodes": 8,
    "autoscaling": True,
    "compute_class": "default",
    "scale_down_strategy": "IdleOnly",
    "node_labels": {"workload": "training"},
    "node_annotations": {},
    "node_taints": None,
    "gpu_driver_version": None,
    "image": None,
    "prefill": None,
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
        mock_module = _make_module({**NP_PARAMS})
        mock_ansible_cls.return_value = mock_module
        mock_apply.return_value = {"changed": True, "result": {"metadata": {"name": "test-pool"}}}

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool import main
        with pytest.raises(SystemExit):
            main()

        mock_module.exit_json.assert_called_once()
        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestDelete:
    @patch(f"{MODULE_PATH}.apply_resource")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_delete(self, mock_ansible_cls, mock_apply):
        mock_module = _make_module({**NP_PARAMS, "state": "absent"})
        mock_ansible_cls.return_value = mock_module
        mock_apply.return_value = {"changed": True, "result": {}}

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestBuildManifest:
    def test_basic_manifest(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool import build_manifest
        manifest = build_manifest(NP_PARAMS)
        assert manifest["apiVersion"] == "compute.coreweave.com/v1alpha1"
        assert manifest["kind"] == "NodePool"
        assert manifest["spec"]["instanceType"] == "gd-8xa100-i128"
        assert manifest["spec"]["targetNodes"] == 4
        assert manifest["spec"]["autoscaling"] is True
        assert manifest["spec"]["nodeLabels"] == {"workload": "training"}

    def test_manifest_with_gpu_driver(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool import build_manifest
        params = {**NP_PARAMS, "gpu_driver_version": "550"}
        manifest = build_manifest(params)
        assert manifest["spec"]["gpu"]["version"] == "550"

    def test_manifest_with_prefill(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool import build_manifest
        params = {**NP_PARAMS, "autoscaling": False, "prefill": {"enabled": True, "timeout": "12h", "max_nodes": 2}}
        manifest = build_manifest(params)
        assert manifest["spec"]["prefill"]["enabled"] is True
        assert manifest["spec"]["prefill"]["timeout"] == "12h"
        assert manifest["spec"]["prefill"]["maxNodes"] == 2

    def test_manifest_with_image(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool import build_manifest
        params = {**NP_PARAMS, "image": {"name": "custom-image", "kernel": None, "release_train": "stable"}}
        manifest = build_manifest(params)
        assert manifest["spec"]["image"]["name"] == "custom-image"
