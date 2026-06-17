"""Unit tests for CoreWeave Object Storage modules."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

KEY_MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_key"
KEY_INFO_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_key_info"
POLICY_MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_policy"
POLICY_INFO_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_policy_info"
BUCKET_INFO_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_bucket_info"


def make_module(params_override=None):
    base = {
        "state": "present",
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


class TestAccessKeyCreate:
    @patch(f"{KEY_MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{KEY_MODULE_PATH}.AnsibleModule")
    def test_create_permanent_key(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"duration_seconds": 0, "access_key_id": None})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.create.return_value = {"accessKeyId": "AK123", "secretAccessKey": "secret"}
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_key import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True
        assert mock_module.exit_json.call_args[1]["access_key"]["accessKeyId"] == "AK123"

    @patch(f"{KEY_MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{KEY_MODULE_PATH}.AnsibleModule")
    def test_create_check_mode(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"duration_seconds": 0, "access_key_id": None})
        mock_module.check_mode = True
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_key import main
        with pytest.raises(SystemExit):
            main()

        mock_api.create.assert_not_called()


class TestAccessKeyRevoke:
    @patch(f"{KEY_MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{KEY_MODULE_PATH}.AnsibleModule")
    def test_revoke_key(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"state": "absent", "access_key_id": "AK123", "duration_seconds": 0})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.create.return_value = {}
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_key import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestAccessKeyInfo:
    @patch(f"{KEY_INFO_PATH}.CoreWeaveAPI")
    @patch(f"{KEY_INFO_PATH}.AnsibleModule")
    def test_list_keys(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"access_key_id": None})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = [{"accessKeyId": "AK1"}, {"accessKeyId": "AK2"}]
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_key_info import main
        with pytest.raises(SystemExit):
            main()

        assert len(mock_module.exit_json.call_args[1]["access_keys"]) == 2


class TestPolicyCreate:
    @patch(f"{POLICY_MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{POLICY_MODULE_PATH}.AnsibleModule")
    def test_create_policy(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({
            "name": "test-policy",
            "policy": {"Version": "2012-10-17", "Statement": []},
        })
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.create.return_value = {"name": "test-policy"}
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_policy import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestPolicyDelete:
    @patch(f"{POLICY_MODULE_PATH}.CoreWeaveAPI")
    @patch(f"{POLICY_MODULE_PATH}.AnsibleModule")
    def test_delete_policy(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"state": "absent", "name": "test-policy", "policy": None})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.delete.return_value = True
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_policy import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["changed"] is True


class TestPolicyInfo:
    @patch(f"{POLICY_INFO_PATH}.CoreWeaveAPI")
    @patch(f"{POLICY_INFO_PATH}.AnsibleModule")
    def test_list_policies(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module()
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = [{"name": "pol-1"}]
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_policy_info import main
        with pytest.raises(SystemExit):
            main()

        assert len(mock_module.exit_json.call_args[1]["policies"]) == 1


class TestBucketInfo:
    @patch(f"{BUCKET_INFO_PATH}.CoreWeaveAPI")
    @patch(f"{BUCKET_INFO_PATH}.AnsibleModule")
    def test_list_buckets(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"bucket_name": None})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.list.return_value = [{"name": "bucket-1"}]
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_bucket_info import main
        with pytest.raises(SystemExit):
            main()

        assert len(mock_module.exit_json.call_args[1]["buckets"]) == 1

    @patch(f"{BUCKET_INFO_PATH}.CoreWeaveAPI")
    @patch(f"{BUCKET_INFO_PATH}.AnsibleModule")
    def test_get_specific_bucket(self, mock_ansible_cls, mock_api_cls):
        mock_module = make_module({"bucket_name": "my-bucket"})
        mock_ansible_cls.return_value = mock_module
        mock_api = MagicMock()
        mock_api.get.return_value = {"name": "my-bucket", "region": "LAS1"}
        mock_api_cls.return_value = mock_api

        from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_object_storage_bucket_info import main
        with pytest.raises(SystemExit):
            main()

        assert mock_module.exit_json.call_args[1]["buckets"][0]["name"] == "my-bucket"
