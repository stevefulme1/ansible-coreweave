#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_vpc
short_description: Manage CoreWeave Virtual Private Clouds
version_added: "0.2.0"
description:
  - Create, update, or delete VPCs via the CoreWeave REST API.
  - VPCs provide isolated networks for CKS clusters.
  - Uses the C(/v1beta1/networking/vpcs) API endpoint.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the VPC.
      - Maximum 30 characters.
    type: str
    required: true
  state:
    description:
      - Desired state of the VPC.
    type: str
    choices:
      - present
      - absent
    default: present
  zone:
    description:
      - Availability zone for the VPC.
      - Required when creating a new VPC.
    type: str
  host_prefix:
    description:
      - IPv4 CIDR for host allocation.
      - Typically a /18 range.
    type: str
  prefixes:
    description:
      - List of additional CIDR prefix configurations.
      - Each entry is a dict with C(value) (CIDR range) and C(purpose).
    type: list
    elements: dict
    suboptions:
      value:
        description: CIDR range value.
        type: str
        required: true
      purpose:
        description: Purpose of this prefix (e.g., pod-cidr, svc-cidr).
        type: str
        required: true
  ingress:
    description:
      - Ingress traffic configuration.
    type: dict
    suboptions:
      disable_public_services:
        description: Prevent public prefix advertisement from nodes.
        type: bool
        default: false
  egress:
    description:
      - Egress traffic configuration.
    type: dict
    suboptions:
      disable_public_access:
        description: Block consumption of public Internet.
        type: bool
        default: false
  dhcp:
    description:
      - DHCP configuration.
    type: dict
    suboptions:
      dns_servers:
        description: Custom DNS server addresses.
        type: list
        elements: str
  wait:
    description:
      - Whether to wait for the VPC to reach READY state.
    type: bool
    default: true
  wait_timeout:
    description:
      - Maximum time in seconds to wait.
    type: int
    default: 1200
extends_documentation_fragment:
  - stevefulme1.coreweave.auth.REST
"""

EXAMPLES = r"""
- name: Create a VPC
  stevefulme1.coreweave.coreweave_vpc:
    api_token: "{{ coreweave_token }}"
    name: ml-network
    zone: LAS1
    host_prefix: "10.0.0.0/18"
    prefixes:
      - value: "10.128.0.0/16"
        purpose: pod-cidr
      - value: "10.96.0.0/16"
        purpose: svc-cidr
      - value: "10.64.0.0/20"
        purpose: lb-cidr
    state: present

- name: Create a VPC with custom DNS
  stevefulme1.coreweave.coreweave_vpc:
    api_token: "{{ coreweave_token }}"
    name: isolated-network
    zone: ORD1
    host_prefix: "10.1.0.0/18"
    dhcp:
      dns_servers:
        - "8.8.8.8"
        - "8.8.4.4"
    state: present

- name: Delete a VPC
  stevefulme1.coreweave.coreweave_vpc:
    api_token: "{{ coreweave_token }}"
    name: ml-network
    state: absent
"""

RETURN = r"""
vpc:
  description: The VPC resource after the operation.
  type: dict
  returned: success
  sample:
    id: vpc-abc123
    name: ml-network
    zone: LAS1
    status: READY
changed:
  description: Whether the resource was changed.
  type: bool
  returned: always
"""

import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.coreweave_api import (
    REST_AUTH_ARGS,
    CoreWeaveAPI,
    CoreWeaveAPIError,
)

VPC_BASE_PATH = "/v1beta1/networking/vpcs"


def find_vpc_by_name(api: CoreWeaveAPI, name: str) -> dict | None:
    """Find a VPC by name from the list endpoint."""
    vpcs = api.list(VPC_BASE_PATH)
    for vpc in vpcs:
        if vpc.get("name") == name:
            return vpc
    return None


def build_create_payload(params: dict) -> dict:
    """Build VPC creation payload from module params."""
    payload: dict = {"name": params["name"]}

    if params.get("zone"):
        payload["zone"] = params["zone"]

    if params.get("host_prefix"):
        payload["hostPrefix"] = params["host_prefix"]

    if params.get("prefixes"):
        payload["prefixes"] = [
            {"value": p["value"], "purpose": p["purpose"]}
            for p in params["prefixes"]
        ]

    if params.get("ingress"):
        payload["ingress"] = {
            "disablePublicServices": params["ingress"].get("disable_public_services", False),
        }

    if params.get("egress"):
        payload["egress"] = {
            "disablePublicAccess": params["egress"].get("disable_public_access", False),
        }

    if params.get("dhcp"):
        dhcp_config: dict = {}
        if params["dhcp"].get("dns_servers"):
            dhcp_config["dnsServers"] = params["dhcp"]["dns_servers"]
        if dhcp_config:
            payload["dhcp"] = dhcp_config

    return payload


def build_update_payload(params: dict) -> dict:
    """Build VPC update payload (only mutable fields)."""
    payload: dict = {}

    if params.get("ingress"):
        payload["ingress"] = {
            "disablePublicServices": params["ingress"].get("disable_public_services", False),
        }

    if params.get("egress"):
        payload["egress"] = {
            "disablePublicAccess": params["egress"].get("disable_public_access", False),
        }

    if params.get("dhcp"):
        dhcp_config: dict = {}
        if params["dhcp"].get("dns_servers"):
            dhcp_config["dnsServers"] = params["dhcp"]["dns_servers"]
        if dhcp_config:
            payload["dhcp"] = dhcp_config

    return payload


def wait_for_ready(api: CoreWeaveAPI, vpc_id: str, timeout: int) -> dict:
    """Poll VPC status until READY or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        vpc = api.get(f"{VPC_BASE_PATH}/{vpc_id}")
        if vpc and vpc.get("status") == "READY":
            return vpc
        time.sleep(10)
    return vpc or {}


def main() -> None:
    """Module entrypoint."""
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        zone=dict(type="str"),
        host_prefix=dict(type="str"),
        prefixes=dict(
            type="list",
            elements="dict",
            options=dict(
                value=dict(type="str", required=True),
                purpose=dict(type="str", required=True),
            ),
        ),
        ingress=dict(
            type="dict",
            options=dict(
                disable_public_services=dict(type="bool", default=False),
            ),
        ),
        egress=dict(
            type="dict",
            options=dict(
                disable_public_access=dict(type="bool", default=False),
            ),
        ),
        dhcp=dict(
            type="dict",
            options=dict(
                dns_servers=dict(type="list", elements="str"),
            ),
        ),
        wait=dict(type="bool", default=True),
        wait_timeout=dict(type="int", default=1200),
        **REST_AUTH_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    api = CoreWeaveAPI(module)
    state = module.params["state"]
    name = module.params["name"]

    existing = find_vpc_by_name(api, name)

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, vpc={})
        if module.check_mode:
            module.exit_json(changed=True, vpc={})
        vpc_id = existing.get("id", existing.get("name"))
        try:
            api.delete(f"{VPC_BASE_PATH}/{vpc_id}")
        except CoreWeaveAPIError as e:
            module.fail_json(msg=f"Failed to delete VPC '{name}': {e.message}")
        module.exit_json(changed=True, vpc={})

    # state == present
    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True, vpc=build_create_payload(module.params))
        payload = build_create_payload(module.params)
        try:
            result = api.create(VPC_BASE_PATH, payload)
        except CoreWeaveAPIError as e:
            module.fail_json(msg=f"Failed to create VPC '{name}': {e.message}")

        if module.params["wait"]:
            vpc_id = result.get("id", result.get("name"))
            result = wait_for_ready(api, vpc_id, module.params["wait_timeout"])

        module.exit_json(changed=True, vpc=result)

    # Update existing
    update_payload = build_update_payload(module.params)
    if not update_payload:
        module.exit_json(changed=False, vpc=existing)

    if module.check_mode:
        module.exit_json(changed=True, vpc=existing)

    vpc_id = existing.get("id", existing.get("name"))
    try:
        result = api.update(f"{VPC_BASE_PATH}/{vpc_id}", update_payload)
    except CoreWeaveAPIError as e:
        module.fail_json(msg=f"Failed to update VPC '{name}': {e.message}")

    if module.params["wait"]:
        result = wait_for_ready(api, vpc_id, module.params["wait_timeout"])

    module.exit_json(changed=True, vpc=result)


if __name__ == "__main__":
    main()
