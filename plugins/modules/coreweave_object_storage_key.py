#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_object_storage_key
short_description: Manage CoreWeave Object Storage access keys
version_added: "0.2.0"
description:
  - Create or revoke access keys for CoreWeave AI Object Storage.
  - Access keys are generated from a Cloud token via the C(/v1/cwobject/access-key) endpoint.
  - Keys can be permanent or time-limited based on C(duration_seconds).
author:
  - Steve Fulmer (@stevefulme1)
options:
  state:
    description:
      - C(present) creates a new access key.
      - C(absent) revokes an existing access key by ID.
    type: str
    choices:
      - present
      - absent
    default: present
  access_key_id:
    description:
      - ID of the access key to revoke.
      - Required when C(state=absent).
    type: str
  duration_seconds:
    description:
      - Lifetime of the access key in seconds.
      - Set to C(0) for a permanent key.
    type: int
    default: 0
extends_documentation_fragment:
  - stevefulme1.coreweave.auth.REST
"""

EXAMPLES = r"""
- name: Create a permanent access key
  stevefulme1.coreweave.coreweave_object_storage_key:
    api_token: "{{ coreweave_token }}"
    duration_seconds: 0
    state: present
  register: key_result

- name: Create a time-limited access key (1 hour)
  stevefulme1.coreweave.coreweave_object_storage_key:
    api_token: "{{ coreweave_token }}"
    duration_seconds: 3600
    state: present
  register: temp_key

- name: Revoke an access key
  stevefulme1.coreweave.coreweave_object_storage_key:
    api_token: "{{ coreweave_token }}"
    access_key_id: AKIAEXAMPLE123
    state: absent
"""

RETURN = r"""
access_key:
  description: The created access key details.
  type: dict
  returned: when state=present
  sample:
    accessKeyId: AKIAEXAMPLE123
    secretAccessKey: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
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

ACCESS_KEY_PATH = "/v1/cwobject/access-key"
REVOKE_BY_KEY_PATH = "/v1/cwobject/revoke-access-key/access-key"


def main() -> None:
    """Module entrypoint."""
    argument_spec = dict(
        state=dict(type="str", choices=["present", "absent"], default="present"),
        access_key_id=dict(type="str"),
        duration_seconds=dict(type="int", default=0),
        **REST_AUTH_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ("access_key_id",)),
        ],
    )

    api = CoreWeaveAPI(module)
    state = module.params["state"]

    if state == "present":
        if module.check_mode:
            module.exit_json(changed=True, access_key={})
        payload = {"durationSeconds": module.params["duration_seconds"]}
        try:
            result = api.create(ACCESS_KEY_PATH, payload)
        except CoreWeaveAPIError as e:
            module.fail_json(msg=f"Failed to create access key: {e.message}")
        module.exit_json(changed=True, access_key=result)

    # state == absent
    if module.check_mode:
        module.exit_json(changed=True, access_key={})
    try:
        api.create(REVOKE_BY_KEY_PATH, {"accessKeyId": module.params["access_key_id"]})
    except CoreWeaveAPIError as e:
        if e.status_code == 404:
            module.exit_json(changed=False, access_key={})
        module.fail_json(msg=f"Failed to revoke access key: {e.message}")
    module.exit_json(changed=True, access_key={})


if __name__ == "__main__":
    main()
