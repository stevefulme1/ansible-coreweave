#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

DOCUMENTATION = r"""
---
module: coreweave_object_storage_bucket_info
short_description: Retrieve CoreWeave Object Storage bucket information
version_added: "0.2.0"
description:
  - List buckets or get details for a specific bucket.
  - Uses the C(/v1/cwobject/bucket-info) API endpoint.
author:
  - Steve Fulmer (@stevefulme1)
options:
  bucket_name:
    description:
      - Name of a specific bucket to retrieve.
      - If omitted, all buckets are listed.
    type: str
extends_documentation_fragment:
  - stevefulme1.coreweave.auth.REST
"""

EXAMPLES = r"""
- name: List all buckets
  stevefulme1.coreweave.coreweave_object_storage_bucket_info:
    api_token: "{{ coreweave_token }}"
  register: all_buckets

- name: Get a specific bucket
  stevefulme1.coreweave.coreweave_object_storage_bucket_info:
    api_token: "{{ coreweave_token }}"
    bucket_name: ml-training-data
  register: bucket_info
"""

RETURN = r"""
buckets:
  description: List of bucket information.
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

BUCKET_INFO_PATH = "/v1/cwobject/bucket-info"


def main() -> None:
    """Module entrypoint."""
    argument_spec = dict(
        bucket_name=dict(type="str"),
        **REST_AUTH_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    api = CoreWeaveAPI(module)
    bucket_name = module.params.get("bucket_name")

    try:
        if bucket_name:
            result = api.get(f"{BUCKET_INFO_PATH}/{bucket_name}")
            buckets = [result] if result else []
        else:
            buckets = api.list(BUCKET_INFO_PATH)
    except CoreWeaveAPIError as e:
        module.fail_json(msg=f"Failed to retrieve bucket info: {e.message}")

    module.exit_json(changed=False, buckets=buckets)


if __name__ == "__main__":
    main()
