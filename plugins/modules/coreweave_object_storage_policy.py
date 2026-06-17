#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_object_storage_policy
short_description: Manage CoreWeave Object Storage access policies
version_added: "0.2.0"
description:
  - Create or delete access policies for CoreWeave AI Object Storage.
  - Uses the C(/v1/cwobject/access-policy) API endpoint.
  - The C(EnsureAccessPolicy) endpoint is idempotent — it creates or updates.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the access policy.
    type: str
    required: true
  state:
    description:
      - C(present) creates or updates the access policy.
      - C(absent) deletes the access policy.
    type: str
    choices:
      - present
      - absent
    default: present
  policy:
    description:
      - The access policy document as a dict.
      - Required when C(state=present).
    type: dict
extends_documentation_fragment:
  - stevefulme1.coreweave.auth.REST
"""

EXAMPLES = r"""
- name: Create an access policy
  stevefulme1.coreweave.coreweave_object_storage_policy:
    api_token: "{{ coreweave_token }}"
    name: ml-data-policy
    policy:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - "s3:GetObject"
            - "s3:PutObject"
          Resource: "arn:aws:s3:::ml-data/*"
    state: present

- name: Delete an access policy
  stevefulme1.coreweave.coreweave_object_storage_policy:
    api_token: "{{ coreweave_token }}"
    name: ml-data-policy
    state: absent
"""

RETURN = r"""
policy:
  description: The access policy after the operation.
  type: dict
  returned: when state=present
changed:
  description: Whether the resource was changed.
  type: bool
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
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        policy=dict(type="dict"),
        **REST_AUTH_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("policy",)),
        ],
    )

    api = CoreWeaveAPI(module)
    state = module.params["state"]
    name = module.params["name"]

    if state == "present":
        if module.check_mode:
            module.exit_json(changed=True, policy={})
        payload = {
            "name": name,
            "policy": module.params["policy"],
        }
        try:
            result = api.create(POLICY_PATH, payload)
        except CoreWeaveAPIError as e:
            module.fail_json(msg=f"Failed to ensure access policy '{name}': {e.message}")
        module.exit_json(changed=True, policy=result or {})

    # state == absent
    if module.check_mode:
        module.exit_json(changed=True, policy={})
    try:
        deleted = api.delete(f"{POLICY_PATH}/{name}")
    except CoreWeaveAPIError as e:
        module.fail_json(msg=f"Failed to delete access policy '{name}': {e.message}")
    module.exit_json(changed=deleted, policy={})


if __name__ == "__main__":
    main()
