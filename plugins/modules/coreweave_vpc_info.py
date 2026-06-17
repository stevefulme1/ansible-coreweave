#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_vpc_info
short_description: Retrieve CoreWeave VPC information
version_added: "0.2.0"
description:
  - Retrieve information about CoreWeave Virtual Private Clouds via the REST API.
  - Can fetch a single VPC by name or list all VPCs.
  - Uses the C(/v1beta1/networking/vpcs) API endpoint.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific VPC to retrieve.
      - If omitted, all VPCs are returned.
    type: str
extends_documentation_fragment:
  - stevefulme1.coreweave.auth.REST
"""

EXAMPLES = r"""
- name: List all VPCs
  stevefulme1.coreweave.coreweave_vpc_info:
    api_token: "{{ coreweave_token }}"
  register: all_vpcs

- name: Get a specific VPC
  stevefulme1.coreweave.coreweave_vpc_info:
    api_token: "{{ coreweave_token }}"
    name: ml-network
  register: vpc_info
"""

RETURN = r"""
vpcs:
  description: List of VPC resources.
  type: list
  elements: dict
  returned: always
  sample:
    - id: vpc-abc123
      name: ml-network
      zone: LAS1
      status: READY
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.coreweave_api import (
    REST_AUTH_ARGS,
    CoreWeaveAPI,
    CoreWeaveAPIError,
)

VPC_BASE_PATH = "/v1beta1/networking/vpcs"


def main() -> None:
    """Module entrypoint."""
    argument_spec = dict(
        name=dict(type="str"),
        **REST_AUTH_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    api = CoreWeaveAPI(module)
    name = module.params.get("name")

    try:
        vpcs = api.list(VPC_BASE_PATH)
    except CoreWeaveAPIError as e:
        module.fail_json(msg=f"Failed to list VPCs: {e.message}")

    if name:
        vpcs = [v for v in vpcs if v.get("name") == name]

    module.exit_json(changed=False, vpcs=vpcs)


if __name__ == "__main__":
    main()
