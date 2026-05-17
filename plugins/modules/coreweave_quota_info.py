#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""coreweave_quota_info module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_quota_info
short_description: Retrieve CoreWeave resource quotas
description:
    - Retrieve resource quota details from CoreWeave.
    - Read-only module.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    host:
        description: API host address.
        type: str
        required: true
    quota_name:
        description: ID of a specific quota.
        type: str
    name:
        description: Filter by name.
        type: str
    username:
        description: Authentication username.
        type: str
    password:
        description: Authentication password.
        type: str
    api_key:
        description: API key for authentication.
        type: str
    validate_certs:
        description: Validate SSL certificates.
        type: bool
        default: true
"""

EXAMPLES = r"""
- name: List all resource quotas
  stevefulme1.coreweave.coreweave_quota_info:
    host: api.example.com
  register: result

- name: Get a specific quota
  stevefulme1.coreweave.coreweave_quota_info:
    host: api.example.com
    quota_name: "example-id"
  register: result
"""

RETURN = r"""
quotas:
    description: List of resource details.
    returned: always
    type: list
    elements: dict
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.stevefulme1.coreweave.plugins.module_utils.api_client import ApiClient
    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            quota_name=dict(type="str"),
            name=dict(type="str"),
            host=dict(type="str", required=True),
            username=dict(type="str"),
            password=dict(type="str", no_log=True),
            api_key=dict(type="str", no_log=True),
            validate_certs=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
    )

    if not HAS_CLIENT:
        module.fail_json(msg="Required Python libraries not found.")

    client = ApiClient(module)
    resource_id = module.params.get("quota_name")

    if resource_id:
        result = client.get("quota", resource_id)
        resources = [result] if result else []
    else:
        resources = client.list("quota", module.params)

    module.exit_json(changed=False, quotas=resources)


if __name__ == "__main__":
    main()
