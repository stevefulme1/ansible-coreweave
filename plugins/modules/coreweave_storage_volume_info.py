#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)

"""Ansible module: coreweave_storage_volume_info."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_storage_volume_info
short_description: Retrieve storage volume information
description:
    - Retrieve details about storage volumes.
    - This is a read-only module.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    volume_name:
        description: ID of a specific storage volume to retrieve.
        type: str
    name:
        description: Filter by name.
        type: str
"""

EXAMPLES = r"""
- name: List all storage volumes
  stevefulme1.coreweave.coreweave_storage_volume_info:
  register: result

- name: Get a specific storage volume
  stevefulme1.coreweave.coreweave_storage_volume_info:
    volume_name: "example-id"
  register: result
"""

RETURN = r"""
storage_volumes:
    description: List of storage volume details.
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
            volume_name=dict(type="str"),
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
    resource_id = module.params.get("volume_name")

    if resource_id:
        result = client.get("storage_volume", resource_id)
        resources = [result] if result else []
    else:
        resources = client.list("storage_volume", module.params)

    module.exit_json(changed=False, storage_volumes=resources)


if __name__ == "__main__":
    main()
