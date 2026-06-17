"""Unit tests for coreweave_vpc module."""

from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type


from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_vpc"


def make_module(params_override=None):
    base = {
        "name": "test-vpc",
        "state": "present",
        "zone": "LAS1",
        "host_prefix": "10.0.0.0/18",
        "prefixes": [{"value": "10.128.0.0/16", "purpose": "pod-cidr"}],
        "ingress": None,
        "egress": None,
        "dhcp": None,
        "wait": False,
        "wait_timeout": 1200,
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


class TestCreate:
    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_create_vpc(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module()
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = []
        mock_api.create.return_value = {"id": "vpc-123", "name": "test-vpc", "status": "CREATING"}
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_vpc import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True

    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_create_check_mode(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module()
        mock_module.check_mode = True
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = []
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_vpc import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True
        mock_api.create.assert_not_called()


class TestDelete:
    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_delete_existing(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"state": "absent"})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = [{"id": "vpc-123", "name": "test-vpc"}]
        mock_api.delete.return_value = True
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_vpc import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True

    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_delete_nonexistent(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"state": "absent"})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = []
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_vpc import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is False


class TestBuildPayload:
    def test_basic_payload(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_vpc import build_create_payload
        params = {
            "name": "test",
            "zone": "LAS1",
            "host_prefix": "10.0.0.0/18",
            "prefixes": [{"value": "10.128.0.0/16", "purpose": "pod-cidr"}],
            "ingress": None,
            "egress": None,
            "dhcp": None,
        }
        payload = build_create_payload(params)
        assert payload["name"] == "test"
        assert payload["zone"] == "LAS1"
        assert payload["hostPrefix"] == "10.0.0.0/18"
        assert len(payload["prefixes"]) == 1

    def test_payload_with_dhcp(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_vpc import build_create_payload
        params = {
            "name": "test",
            "zone": "ORD1",
            "host_prefix": None,
            "prefixes": None,
            "ingress": None,
            "egress": None,
            "dhcp": {"dns_servers": ["8.8.8.8", "8.8.4.4"]},
        }
        payload = build_create_payload(params)
        assert payload["dhcp"]["dnsServers"] == ["8.8.8.8", "8.8.4.4"]
