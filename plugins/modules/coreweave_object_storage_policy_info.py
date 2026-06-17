#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_object_storage_policy_info
short_description: Retrieve CoreWeave Object Storage access policy information
version_added: "0.2.0"
description:
  - List access policies for CoreWeave AI Object Storage.
  - Uses the C(/v1/cwobject/access-policy) API endpoint.
author:
  - Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.coreweave.auth.REST
"""

EXAMPLES = r"""
- name: List all access policies
  stevefulme1.coreweave.coreweave_object_storage_policy_info:
    api_token: "{{ coreweave_token }}"
  register: policies
"""

RETURN = r"""
policies:
  description: List of access policies.
  type: list
  elements: dict
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.coreweave_api import (
    REST_AUTH_ARGS,
    CoreWeaveAPI,
    CoreWeaveAPIError,
)

POLICY_PATH = "/v1/cwobject/access-policy"


def main() -> None:
    """Module entrypoint."""
    argument_spec = dict(**REST_AUTH_ARGS)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    api = CoreWeaveAPI(module)

    try:
        policies = api.list(POLICY_PATH)
    except CoreWeaveAPIError as e:
        module.fail_json(msg=f"Failed to list access policies: {e.message}")

    module.exit_json(changed=False, policies=policies)


if __name__ == "__main__":
    main()
