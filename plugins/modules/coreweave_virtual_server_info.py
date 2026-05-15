#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)

"""Ansible module: coreweave_virtual_server_info."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_virtual_server_info
short_description: Retrieve virtual server information
description:
    - Retrieve details about virtual servers.
    - This is a read-only module.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    server_name:
        description: ID of a specific virtual server to retrieve.
        type: str
    name:
        description: Filter by name.
        type: str
"""

EXAMPLES = r"""
- name: List all virtual servers
  stevefulme1.coreweave.coreweave_virtual_server_info:
  register: result

- name: Get a specific virtual server
  stevefulme1.coreweave.coreweave_virtual_server_info:
    server_name: "example-id"
  register: result
"""

RETURN = r"""
virtual_servers:
    description: List of virtual server details.
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
            server_name=dict(type="str"),
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
    resource_id = module.params.get("server_name")

    if resource_id:
        result = client.get("virtual_server", resource_id)
        resources = [result] if result else []
    else:
        resources = client.list("virtual_server", module.params)

    module.exit_json(changed=False, virtual_servers=resources)


if __name__ == "__main__":
    main()
