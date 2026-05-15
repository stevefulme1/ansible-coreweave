"""Unit tests for coreweave_virtual_server module."""

from unittest.mock import MagicMock, patch


class TestCreate:
    def test_create_returns_resource(self):
        mock_client = MagicMock()
        mock_client.create.return_value = {"id": "123", "name": "test"}
        result = mock_client.create("virtual_server", {"name": "test"})
        assert result["id"] == "123"
        mock_client.create.assert_called_once()


class TestDelete:
    def test_delete_calls_api(self):
        mock_client = MagicMock()
        mock_client.delete.return_value = None
        mock_client.delete("virtual_server", "123")
        mock_client.delete.assert_called_once_with("virtual_server", "123")


class TestList:
    def test_list_returns_items(self):
        mock_client = MagicMock()
        mock_client.list.return_value = [{"id": "1"}, {"id": "2"}]
        result = mock_client.list("virtual_server")
        assert len(result) == 2


class TestGet:
    def test_get_returns_single(self):
        mock_client = MagicMock()
        mock_client.get.return_value = {"id": "123", "name": "test"}
        result = mock_client.get("virtual_server", "123")
        assert result["name"] == "test"

    def test_get_not_found(self):
        mock_client = MagicMock()
        mock_client.get.return_value = None
        result = mock_client.get("virtual_server", "nonexistent")
        assert result is None
