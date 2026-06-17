"""Unit tests for CoreWeave inventory plugin."""

from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

from unittest.mock import MagicMock, patch

PLUGIN_PATH = "ansible_collections.stevefulme1.coreweave.plugins.inventory.coreweave"


class TestVerifyFile:
    @patch("ansible.plugins.inventory.BaseInventoryPlugin.verify_file", return_value=True)
    def test_valid_extension(self, mock_super):
        from ansible_collections.stevefulme1.coreweave.plugins.inventory.coreweave import InventoryModule
        plugin = InventoryModule()
        assert plugin.verify_file("/path/to/hosts.coreweave.yml") is True

    @patch("ansible.plugins.inventory.BaseInventoryPlugin.verify_file", return_value=True)
    def test_valid_yaml_extension(self, mock_super):
        from ansible_collections.stevefulme1.coreweave.plugins.inventory.coreweave import InventoryModule
        plugin = InventoryModule()
        assert plugin.verify_file("/path/to/hosts.coreweave.yaml") is True

    @patch("ansible.plugins.inventory.BaseInventoryPlugin.verify_file", return_value=True)
    def test_invalid_extension(self, mock_super):
        from ansible_collections.stevefulme1.coreweave.plugins.inventory.coreweave import InventoryModule
        plugin = InventoryModule()
        assert plugin.verify_file("/path/to/hosts.yml") is False

    @patch("ansible.plugins.inventory.BaseInventoryPlugin.verify_file", return_value=False)
    def test_base_rejects(self, mock_super):
        from ansible_collections.stevefulme1.coreweave.plugins.inventory.coreweave import InventoryModule
        plugin = InventoryModule()
        assert plugin.verify_file("/path/to/hosts.coreweave.yml") is False


class TestGetClusters:
    @patch(f"{PLUGIN_PATH}.open_url")
    def test_list_clusters(self, mock_open_url):
        from ansible_collections.stevefulme1.coreweave.plugins.inventory.coreweave import InventoryModule
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"clusters": [{"name": "c1", "zone": "LAS1"}, {"name": "c2", "zone": "ORD1"}]}'
        mock_open_url.return_value = mock_response

        plugin = InventoryModule()
        clusters = plugin._get_clusters("https://api.coreweave.com", "test-token")
        assert len(clusters) == 2
        assert clusters[0]["name"] == "c1"

    @patch(f"{PLUGIN_PATH}.open_url")
    def test_list_clusters_array_response(self, mock_open_url):
        from ansible_collections.stevefulme1.coreweave.plugins.inventory.coreweave import InventoryModule
        mock_response = MagicMock()
        mock_response.read.return_value = b'[{"name": "c1"}]'
        mock_open_url.return_value = mock_response

        plugin = InventoryModule()
        clusters = plugin._get_clusters("https://api.coreweave.com", "token")
        assert len(clusters) == 1
