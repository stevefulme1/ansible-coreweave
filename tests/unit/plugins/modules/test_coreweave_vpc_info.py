"""Unit tests for coreweave_vpc_info module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_vpc_info"


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


class TestListVPCs:
    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_list_all(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module()
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = [{"name": "vpc-1"}, {"name": "vpc-2"}]
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_vpc_info import main
        with pytest.raises(SystemExit):
            main()

        call_kwargs = mock_module.exit_json.call_args[1]
        assert len(call_kwargs["vpcs"]) == 2

    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_filter_by_name(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"name": "vpc-1"})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = [{"name": "vpc-1"}, {"name": "vpc-2"}]
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_vpc_info import main
        with pytest.raises(SystemExit):
            main()

        call_kwargs = mock_module.exit_json.call_args[1]
        assert len(call_kwargs["vpcs"]) == 1
