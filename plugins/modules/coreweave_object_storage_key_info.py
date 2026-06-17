#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_object_storage_key_info
short_description: Retrieve CoreWeave Object Storage access key information
version_added: "0.2.0"
description:
  - List access keys or get details for a specific access key.
  - Uses the C(/v1/cwobject/access-key) API endpoint.
author:
  - Steve Fulmer (@stevefulme1)
options:
  access_key_id:
    description:
      - ID of a specific access key to retrieve.
      - If omitted, all access keys are listed.
    type: str
extends_documentation_fragment:
  - stevefulme1.coreweave.auth.REST
"""

EXAMPLES = r"""
- name: List all access keys
  stevefulme1.coreweave.coreweave_object_storage_key_info:
    api_token: "{{ coreweave_token }}"
  register: all_keys

- name: Get a specific access key
  stevefulme1.coreweave.coreweave_object_storage_key_info:
    api_token: "{{ coreweave_token }}"
    access_key_id: AKIAEXAMPLE123
  register: key_info
"""

RETURN = r"""
access_keys:
  description: List of access key information.
  type: list
  elements: dict
  returned: always
  sample:
    - accessKeyId: AKIAEXAMPLE123
      status: Active
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.coreweave_api import (
    REST_AUTH_ARGS,
    CoreWeaveAPI,
    CoreWeaveAPIError,
)

ACCESS_KEY_PATH = "/v1/cwobject/access-key"


def main() -> None:
    """Module entrypoint."""
    argument_spec = dict(
        access_key_id=dict(type="str"),
        **REST_AUTH_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    api = CoreWeaveAPI(module)
    access_key_id = module.params.get("access_key_id")

    try:
        if access_key_id:
            result = api.get(f"{ACCESS_KEY_PATH}/{access_key_id}")
            keys = [result] if result else []
        else:
            keys = api.list(ACCESS_KEY_PATH)
    except CoreWeaveAPIError as e:
        module.fail_json(msg=f"Failed to retrieve access keys: {e.message}")

    module.exit_json(changed=False, access_keys=keys)


if __name__ == "__main__":
    main()
