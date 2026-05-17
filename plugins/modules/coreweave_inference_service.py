#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: coreweave_inference_service."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_inference_service
short_description: Manage CoreWeave inference endpoints
description:
    - Manage CoreWeave inference endpoints in Coreweave.
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
    host:
        description: API host address.
        type: str
        required: true
    username:
        description: Authentication username.
        type: str
    password:
        description: Authentication password.
        type: str
        no_log: true
    api_key:
        description: API key for authentication.
        type: str
        no_log: true
    validate_certs:
        description: Whether to validate SSL certificates.
        type: bool
        default: true
"""

EXAMPLES = r"""
- name: Create a inference service
  stevefulme1.coreweave.coreweave_inference_service:
    name: my-inference-service
    state: present

- name: Delete a inference service
  stevefulme1.coreweave.coreweave_inference_service:
    service_name: "example-id"
    state: absent
"""

RETURN = r"""
inference_service:
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
            service_name=dict(type="str"),
            name=dict(type="str"),
            host=dict(type="str", required=True),
            username=dict(type="str"),
            password=dict(type="str", no_log=True),
            api_key=dict(type="str", no_log=True),
            validate_certs=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ("service_name",)),
        ],
    )

    if not HAS_CLIENT:
        module.fail_json(msg="Required Python libraries not found.")

    client = ApiClient(module)
    state = module.params["state"]
    resource_id = module.params.get("service_name")

    if state == "present":
        existing = None
        if resource_id:
            existing = client.get("inference_service", resource_id)
        elif module.params.get("name"):
            candidates = client.list("inference_service", {{"name": module.params["name"]}})
            if candidates:
                existing = candidates[0]

        if existing:
            if module.check_mode:
                module.exit_json(changed=False, inference_service=existing)
            result = client.update("inference_service", resource_id or existing.get("id", ""), module.params)
            module.exit_json(changed=True, inference_service=result)
        else:
            if module.check_mode:
                module.exit_json(changed=True)
            result = client.create("inference_service", module.params)
            module.exit_json(changed=True, inference_service=result)
    else:
        existing = None
        if resource_id:
            existing = client.get("inference_service", resource_id)
        if not existing:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        client.delete("inference_service", resource_id)
        module.exit_json(changed=True)


if __name__ == "__main__":
    main()
