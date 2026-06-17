"""Unit tests for coreweave_cks_cluster_info module."""

from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type


from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster_info"


def make_module(params_override=None):
    base = {
        "name": None,
        "api_token": "test-token",
        "api_url": "https://api.coreweave.com",
        "validate_certs": True,
        "timeout": 60,
    }
    if params_override:
        base.update(params_override)
    module = MagicMock()
    module.params = base
    module.check_mode = False
    module.fail_json = MagicMock(side_effect=SystemExit(1))
    module.exit_json = MagicMock(side_effect=SystemExit(0))
    return module


class TestListClusters:
    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_list_all(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module()
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = [
            {"name": "cluster-1", "status": "STATUS_RUNNING"},
            {"name": "cluster-2", "status": "STATUS_CREATING"},
        ]
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster_info import main
        with pytest.raises(SystemExit):
            main()

        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs["changed"] is False
        assert len(call_kwargs["clusters"]) == 2

    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_filter_by_name(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"name": "cluster-1"})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = [
            {"name": "cluster-1", "status": "STATUS_RUNNING"},
            {"name": "cluster-2", "status": "STATUS_CREATING"},
        ]
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster_info import main
        with pytest.raises(SystemExit):
            main()

        call_kwargs = mock_module.exit_json.call_args[1]
        assert len(call_kwargs["clusters"]) == 1
        assert call_kwargs["clusters"][0]["name"] == "cluster-1"

    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_empty_result(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"name": "nonexistent"})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = []
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster_info import main
        with pytest.raises(SystemExit):
            main()

        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs["clusters"] == []
