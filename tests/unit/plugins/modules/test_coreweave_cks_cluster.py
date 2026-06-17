"""Unit tests for coreweave_cks_cluster module."""

from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type



from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster"
API_PATH = "ansible_collections.stevefulme1.coreweave.plugins.module_utils.coreweave_api"


def make_module(params_override=None):
    """Build a mock AnsibleModule with CKS cluster defaults."""
    base = {
        "name": "test-cluster",
        "state": "present",
        "zone": "LAS1",
        "vpc_id": "vpc-123",
        "version": "v1.32",
        "public": False,
        "pod_cidr_name": "pod-cidr",
        "service_cidr_name": "svc-cidr",
        "internal_lb_cidr_names": ["lb-cidr-1"],
        "oidc": None,
        "wait": False,
        "wait_timeout": 2700,
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
    """Test CKS cluster creation."""

    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_create_new_cluster(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module()
        mock_ansible_cls.return_value = mock_module

        mock_api = MagicMock()
        mock_api.list.return_value = []
        mock_api.create.return_value = {"id": "c-123", "name": "test-cluster", "status": "STATUS_CREATING"}
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster import main
        with pytest.raises(SystemExit):
            main()

        mock_module.exit_json.assert_called_once()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs["changed"] is True
        assert call_kwargs["cluster"]["name"] == "test-cluster"

    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_create_check_mode(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module()
        mock_module.check_mode = True
        mock_ansible_cls.return_value = mock_module

        mock_api = MagicMock()
        mock_api.list.return_value = []
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster import main
        with pytest.raises(SystemExit):
            main()

        mock_module.exit_json.assert_called_once()
        assert mock_module.exit_json.call_args[1]["changed"] is True
        mock_api.create.assert_not_called()


class TestDelete:
    """Test CKS cluster deletion."""

    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_delete_existing(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"state": "absent"})
        mock_ansible_cls.return_value = mock_module

        mock_api = MagicMock()
        mock_api.list.return_value = [{"id": "c-123", "name": "test-cluster"}]
        mock_api.delete.return_value = True
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster import main
        with pytest.raises(SystemExit):
            main()

        mock_module.exit_json.assert_called_once()
        assert mock_module.exit_json.call_args[1]["changed"] is True

    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_delete_nonexistent(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"state": "absent"})
        mock_ansible_cls.return_value = mock_module

        mock_api = MagicMock()
        mock_api.list.return_value = []
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster import main
        with pytest.raises(SystemExit):
            main()

        mock_module.exit_json.assert_called_once()
        assert mock_module.exit_json.call_args[1]["changed"] is False


class TestUpdate:
    """Test CKS cluster update."""

    @patch(f"{MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_update_existing(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"public": True})
        mock_ansible_cls.return_value = mock_module

        mock_api = MagicMock()
        mock_api.list.return_value = [{"id": "c-123", "name": "test-cluster", "public": False}]
        mock_api.update.return_value = {"id": "c-123", "name": "test-cluster", "public": True}
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster import main
        with pytest.raises(SystemExit):
            main()

        mock_module.exit_json.assert_called_once()
        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestBuildPayload:
    """Test payload construction."""

    def test_create_payload_basic(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster import build_create_payload
        params = {
            "name": "test",
            "zone": "LAS1",
            "vpc_id": "vpc-1",
            "version": "v1.32",
            "public": False,
            "pod_cidr_name": "pods",
            "service_cidr_name": "svcs",
            "internal_lb_cidr_names": ["lb1"],
            "oidc": None,
        }
        payload = build_create_payload(params)
        assert payload["name"] == "test"
        assert payload["zone"] == "LAS1"
        assert payload["vpcId"] == "vpc-1"
        assert payload["podCidrName"] == "pods"

    def test_create_payload_with_oidc(self):
        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_cks_cluster import build_create_payload
        params = {
            "name": "test",
            "zone": "LAS1",
            "vpc_id": "vpc-1",
            "version": "v1.32",
            "public": False,
            "pod_cidr_name": "pods",
            "service_cidr_name": "svcs",
            "internal_lb_cidr_names": None,
            "oidc": {
                "issuer_url": "https://auth.example.com",
                "client_id": "my-client",
                "username_claim": None,
                "username_prefix": None,
                "groups_claim": None,
                "groups_prefix": None,
                "ca": None,
            },
        }
        payload = build_create_payload(params)
        assert payload["oidc"]["issuerUrl"] == "https://auth.example.com"
        assert payload["oidc"]["clientId"] == "my-client"
