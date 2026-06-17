# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""REST API client for CoreWeave api.coreweave.com endpoints.

Handles authentication, request building, and error handling for the
CKS, VPC, and Object Storage REST APIs.
"""

from __future__ import annotations

__metaclass__ = type

import json
from typing import TYPE_CHECKING

from ansible.module_utils.urls import open_url

if TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule


class CoreWeaveAPIError(Exception):
    """Raised when the CoreWeave API returns an error."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


class CoreWeaveAPI:
    """REST client for CoreWeave api.coreweave.com.

    Uses ansible.module_utils.urls.open_url to avoid external dependencies.
    Authentication is via Bearer token passed as the api_token module parameter.
    """

    DEFAULT_API_URL = "https://api.coreweave.com"

    def __init__(self, module: AnsibleModule) -> None:
        self.module = module
        self.api_url = module.params.get("api_url") or self.DEFAULT_API_URL
        self.api_url = self.api_url.rstrip("/")
        self.api_token = module.params.get("api_token")
        self.validate_certs = module.params.get("validate_certs", True)
        self.timeout = module.params.get("timeout", 60)

        if not self.api_token:
            module.fail_json(msg="api_token is required for CoreWeave REST API operations.")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, data: dict | None = None) -> dict | None:
        """Make an HTTP request to the CoreWeave API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE).
            path: API path (appended to api_url).
            data: Request body dict (JSON-encoded).

        Returns:
            Parsed JSON response dict, or None for 204/DELETE.

        Raises:
            CoreWeaveAPIError: On non-2xx responses.
        """
        url = f"{self.api_url}{path}"
        body = json.dumps(data).encode("utf-8") if data else None

        try:
            response = open_url(
                url,
                method=method,
                headers=self._headers(),
                data=body,
                validate_certs=self.validate_certs,
                timeout=self.timeout,
            )
            status = response.getcode()
            response_body = response.read().decode("utf-8")
        except Exception as e:
            error_msg = str(e)
            # open_url raises urllib errors with status codes embedded
            if hasattr(e, "code"):
                status = e.code  # type: ignore[attr-defined]
                try:
                    response_body = e.read().decode("utf-8")  # type: ignore[attr-defined]
                except Exception:
                    response_body = error_msg
                if status == 404:
                    return None
                raise CoreWeaveAPIError(status, response_body) from e
            self.module.fail_json(msg=f"CoreWeave API request failed: {error_msg}")

        if status == 204 or (status >= 200 and not response_body):
            return None

        if status >= 400:
            raise CoreWeaveAPIError(status, response_body)

        try:
            return json.loads(response_body)
        except json.JSONDecodeError:
            return {"raw": response_body}

    def get(self, path: str) -> dict | None:
        """GET request. Returns None on 404."""
        return self._request("GET", path)

    def list(self, path: str) -> list:
        """GET request returning a list of items."""
        result = self._request("GET", path)
        if result is None:
            return []
        if isinstance(result, list):
            return result
        # Handle paginated or wrapped responses
        for key in ("clusters", "vpcs", "items", "data", "accessKeys"):
            if key in result:
                return result[key]
        return [result]

    def create(self, path: str, data: dict) -> dict:
        """POST request to create a resource."""
        result = self._request("POST", path, data)
        return result or {}

    def update(self, path: str, data: dict) -> dict:
        """PATCH request to update a resource."""
        result = self._request("PATCH", path, data)
        return result or {}

    def delete(self, path: str) -> bool:
        """DELETE request. Returns True on success, False if not found."""
        try:
            self._request("DELETE", path)
            return True
        except CoreWeaveAPIError as e:
            if e.status_code == 404:
                return False
            raise


# Common argument_spec entries for REST API modules
REST_AUTH_ARGS = dict(
    api_token=dict(type="str", required=True, no_log=True),
    api_url=dict(type="str", default="https://api.coreweave.com"),
    validate_certs=dict(type="bool", default=True),
    timeout=dict(type="int", default=60),
)
