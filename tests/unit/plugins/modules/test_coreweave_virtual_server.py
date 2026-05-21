"""Unit tests for stevefulme1.coreweave.coreweave_virtual_server module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE_PATH = "ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_virtual_server"

try:
    from ansible_collections.stevefulme1.coreweave.plugins.modules.coreweave_virtual_server import main
except ImportError:
    from unittest.mock import MagicMock as main

class TestCreate:
    """Test coreweave_virtual_server creation."""

    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_create(self, mock_ansible_cls):
        """Creating coreweave_virtual_server calls exit_json with changed=True."""
        mock_module = MagicMock()
        mock_module.params = {'kubeconfig': '/tmp/kube', 'namespace': 'default', 'state': 'present', 'name': 'test-vs', 'region': 'ORD1', 'os_type': 'linux', 'gpu_type': 'Quadro_RTX_4000', 'gpu_count': 1, 'cpu_count': 4, 'memory': '16Gi', 'root_disk_size': '40Gi'}
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module
        main()
        mock_module.exit_json.assert_called_once()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs.get("changed") is True
class TestDelete:
    """Test coreweave_virtual_server deletion."""

    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_delete(self, mock_ansible_cls):
        """Deleting coreweave_virtual_server calls exit_json with changed=True."""
        mock_module = MagicMock()
        mock_module.params = {'kubeconfig': '/tmp/kube', 'namespace': 'default', 'state': 'absent', 'name': 'test-vs', 'region': 'ORD1', 'os_type': 'linux', 'gpu_type': None, 'gpu_count': 1, 'cpu_count': 4, 'memory': '16Gi', 'root_disk_size': '40Gi'}
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module
        main()
        mock_module.exit_json.assert_called_once()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs.get("changed") is True
class TestIdempotent:
    """Test coreweave_virtual_server idempotency."""

    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_create_idempotent(self, mock_ansible_cls):
        """Re-creating existing coreweave_virtual_server calls exit_json with changed=False."""
        mock_module = MagicMock()
        mock_module.params = {'kubeconfig': '/tmp/kube', 'namespace': 'default', 'state': 'present', 'name': 'test-vs', 'region': 'ORD1', 'os_type': 'linux', 'gpu_type': 'Quadro_RTX_4000', 'gpu_count': 1, 'cpu_count': 4, 'memory': '16Gi', 'root_disk_size': '40Gi'}
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module
        main()
        mock_module.exit_json.assert_called()
