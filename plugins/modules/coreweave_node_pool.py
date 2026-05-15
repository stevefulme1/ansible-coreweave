#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)

"""Ansible module: coreweave_node_pool."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_node_pool
short_description: CoreWeave GPU node pool information
description:
    - CoreWeave GPU node pool information in Coreweave.
    - Supports create, update, and delete operations.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    state:
        description: Desired state of the resource.
        type: str
        default: present
        choices: [present, absent]
    pool_name:
        description: Unique identifier of the node pool.
        type: str
    name:
        description: Display name of the node pool.
        type: str
"""

EXAMPLES = r"""
- name: Create a node pool
  stevefulme1.coreweave.coreweave_node_pool:
    name: my-node-pool
    state: present

- name: Delete a node pool
  stevefulme1.coreweave.coreweave_node_pool:
    pool_name: "example-id"
    state: absent
"""

RETURN = r"""
node_pool:
    description: Resource details.
    returned: on success
    type: dict
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
            state=dict(type="str", default="present", choices=["present", "absent"]),
            pool_name=dict(type="str"),
            name=dict(type="str"),
            host=dict(type="str", required=True),
            username=dict(type="str"),
            password=dict(type="str", no_log=True),
            api_key=dict(type="str", no_log=True),
            validate_certs=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ("pool_name",)),
        ],
    )

    if not HAS_CLIENT:
        module.fail_json(msg="Required Python libraries not found.")

    client = ApiClient(module)
    state = module.params["state"]
    resource_id = module.params.get("pool_name")

    if state == "present":
        if resource_id:
            result = client.update("node_pool", resource_id, module.params)
        else:
            if module.check_mode:
                module.exit_json(changed=True)
            result = client.create("node_pool", module.params)
        module.exit_json(changed=True, node_pool=result)
    else:
        if module.check_mode:
            module.exit_json(changed=True)
        client.delete("node_pool", resource_id)
        module.exit_json(changed=True)


if __name__ == "__main__":
    main()
