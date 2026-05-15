#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)

"""Ansible module: coreweave_storage_volume."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_storage_volume
short_description: Manage CoreWeave persistent storage volumes
description:
    - Manage CoreWeave persistent storage volumes in Coreweave.
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
    volume_name:
        description: Unique identifier of the storage volume.
        type: str
    name:
        description: Display name of the storage volume.
        type: str
"""

EXAMPLES = r"""
- name: Create a storage volume
  stevefulme1.coreweave.coreweave_storage_volume:
    name: my-storage-volume
    state: present

- name: Delete a storage volume
  stevefulme1.coreweave.coreweave_storage_volume:
    volume_name: "example-id"
    state: absent
"""

RETURN = r"""
storage_volume:
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
            volume_name=dict(type="str"),
            name=dict(type="str"),
            host=dict(type="str", required=True),
            username=dict(type="str"),
            password=dict(type="str", no_log=True),
            api_key=dict(type="str", no_log=True),
            validate_certs=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ("volume_name",)),
        ],
    )

    if not HAS_CLIENT:
        module.fail_json(msg="Required Python libraries not found.")

    client = ApiClient(module)
    state = module.params["state"]
    resource_id = module.params.get("volume_name")

    if state == "present":
        if resource_id:
            result = client.update("storage_volume", resource_id, module.params)
        else:
            if module.check_mode:
                module.exit_json(changed=True)
            result = client.create("storage_volume", module.params)
        module.exit_json(changed=True, storage_volume=result)
    else:
        if module.check_mode:
            module.exit_json(changed=True)
        client.delete("storage_volume", resource_id)
        module.exit_json(changed=True)


if __name__ == "__main__":
    main()
