"""Unit tests for coreweave_node_pool_info module."""

from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool_info"


def _make_module(params):
    module = MagicMock()
    module.params = params
    module.check_mode = False
    module.fail_json = MagicMock(side_effect=SystemExit(1))
    module.exit_json = MagicMock(side_effect=SystemExit(0))
    return module


class TestListNodePools:
    @patch(f"{MODULE_PATH}.list_resources")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_list_all(self, mock_ansible_cls, mock_list):
        params = {"name": None, "namespace": "default", "kubeconfig": None, "context": None,
                  "label_selector": None, "field_selector": None}
        mock_module = _make_module(params)
        mock_ansible_cls.return_value = mock_module
        mock_list.return_value = [{"metadata": {"name": "pool-1"}}, {"metadata": {"name": "pool-2"}}]

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool_info import main
        with pytest.raises(SystemExit):
            main()

        assert len(mock_module.exit_json.call_args[1]["node_pools"]) == 2

    @patch(f"{MODULE_PATH}.get_existing_resource")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_get_by_name(self, mock_ansible_cls, mock_get):
        params = {"name": "pool-1", "namespace": "default", "kubeconfig": None, "context": None,
                  "label_selector": None, "field_selector": None}
        mock_module = _make_module(params)
        mock_ansible_cls.return_value = mock_module
        mock_get.return_value = {"metadata": {"name": "pool-1"}, "spec": {"instanceType": "gd-8xa100-i128"}}

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool_info import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["node_pools"][0]["metadata"]["name"] == "pool-1"

    @patch(f"{MODULE_PATH}.get_existing_resource")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_get_nonexistent(self, mock_ansible_cls, mock_get):
        params = {"name": "missing", "namespace": "default", "kubeconfig": None, "context": None,
                  "label_selector": None, "field_selector": None}
        mock_module = _make_module(params)
        mock_ansible_cls.return_value = mock_module
        mock_get.return_value = None

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_node_pool_info import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["node_pools"] == []
