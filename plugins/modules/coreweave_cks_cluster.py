#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_cks_cluster
short_description: Manage CoreWeave Kubernetes Service (CKS) clusters
version_added: "0.2.0"
description:
  - Create, update, or delete CKS clusters via the CoreWeave REST API.
  - CKS provides managed Kubernetes on bare metal for training, inference,
    and HPC workloads.
  - Uses the C(/v1beta1/cks/clusters) API endpoint.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the CKS cluster.
      - Maximum 30 characters.
    type: str
    required: true
  state:
    description:
      - Desired state of the cluster.
    type: str
    choices:
      - present
      - absent
    default: present
  zone:
    description:
      - Availability zone for the cluster.
    type: str
  vpc_id:
    description:
      - VPC ID to associate with the cluster.
      - Must be in the same zone as the cluster.
    type: str
  version:
    description:
      - Kubernetes minor version.
      - For example, C(v1.32).
    type: str
  public:
    description:
      - Whether the API server is accessible from the internet.
    type: bool
    default: false
  pod_cidr_name:
    description:
      - VPC prefix name for the pod CIDR.
    type: str
  service_cidr_name:
    description:
      - VPC prefix name for the service CIDR.
    type: str
  internal_lb_cidr_names:
    description:
      - VPC prefix names for internal load balancers.
      - This field is append-only; removing CIDRs triggers cluster replacement.
    type: list
    elements: str
  oidc:
    description:
      - OIDC authentication configuration.
    type: dict
    suboptions:
      issuer_url:
        description: OIDC provider URL.
        type: str
        required: true
      client_id:
        description: OIDC client identifier.
        type: str
        required: true
      username_claim:
        description: Username claim field.
        type: str
      username_prefix:
        description: Prefix applied to usernames.
        type: str
      groups_claim:
        description: Group membership claim field.
        type: str
      groups_prefix:
        description: Prefix applied to groups.
        type: str
      ca:
        description: Base64-encoded CA certificate for issuer validation.
        type: str
  wait:
    description:
      - Whether to wait for the cluster to reach RUNNING state.
    type: bool
    default: true
  wait_timeout:
    description:
      - Maximum time in seconds to wait for cluster creation.
    type: int
    default: 2700
extends_documentation_fragment:
  - stevefulme1.coreweave.auth.REST
"""

EXAMPLES = r"""
- name: Create a CKS cluster
  stevefulme1.coreweave.coreweave_cks_cluster:
    api_token: "{{ coreweave_token }}"
    name: ml-training-cluster
    zone: LAS1
    vpc_id: vpc-abc123
    version: v1.32
    public: false
    pod_cidr_name: pod-cidr
    service_cidr_name: svc-cidr
    internal_lb_cidr_names:
      - lb-cidr-1
    state: present

- name: Update cluster to enable public API access
  stevefulme1.coreweave.coreweave_cks_cluster:
    api_token: "{{ coreweave_token }}"
    name: ml-training-cluster
    public: true
    state: present

- name: Delete a CKS cluster
  stevefulme1.coreweave.coreweave_cks_cluster:
    api_token: "{{ coreweave_token }}"
    name: ml-training-cluster
    state: absent
"""

RETURN = r"""
cluster:
  description: The CKS cluster resource after the operation.
  type: dict
  returned: success
  sample:
    id: cluster-abc123
    name: ml-training-cluster
    zone: LAS1
    version: v1.32
    status: STATUS_RUNNING
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

CKS_BASE_PATH = "/v1beta1/cks/clusters"


def find_cluster_by_name(api: CoreWeaveAPI, name: str) -> dict | None:
    """Find a cluster by name from the list endpoint."""
    clusters = api.list(CKS_BASE_PATH)
    for cluster in clusters:
        if cluster.get("name") == name:
            return cluster
    return None


def build_create_payload(params: dict) -> dict:
    """Build the cluster creation payload from module params."""
    payload: dict = {
        "name": params["name"],
    }

    for field in ("zone", "version"):
        if params.get(field):
            payload[field] = params[field]

    if params.get("vpc_id"):
        payload["vpcId"] = params["vpc_id"]

    if params.get("public") is not None:
        payload["public"] = params["public"]

    if params.get("pod_cidr_name"):
        payload["podCidrName"] = params["pod_cidr_name"]

    if params.get("service_cidr_name"):
        payload["serviceCidrName"] = params["service_cidr_name"]

    if params.get("internal_lb_cidr_names"):
        payload["internalLbCidrNames"] = params["internal_lb_cidr_names"]

    if params.get("oidc"):
        oidc = params["oidc"]
        payload["oidc"] = {
            "issuerUrl": oidc["issuer_url"],
            "clientId": oidc["client_id"],
        }
        for key in ("username_claim", "username_prefix", "groups_claim", "groups_prefix", "ca"):
            camel_key = key.replace("_", " ").title().replace(" ", "")
            camel_key = camel_key[0].lower() + camel_key[1:]
            if oidc.get(key):
                payload["oidc"][camel_key] = oidc[key]

    return payload


def build_update_payload(params: dict) -> dict:
    """Build the cluster update (PATCH) payload."""
    payload: dict = {}

    if params.get("version"):
        payload["version"] = params["version"]

    if params.get("public") is not None:
        payload["public"] = params["public"]

    if params.get("oidc"):
        oidc = params["oidc"]
        payload["oidc"] = {
            "issuerUrl": oidc["issuer_url"],
            "clientId": oidc["client_id"],
        }

    if params.get("internal_lb_cidr_names"):
        payload["internalLbCidrNames"] = params["internal_lb_cidr_names"]

    return payload


def wait_for_status(api: CoreWeaveAPI, cluster_id: str, target: str, timeout: int) -> dict:
    """Poll cluster status until target state or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        cluster = api.get(f"{CKS_BASE_PATH}/{cluster_id}")
        if cluster and cluster.get("status") == target:
            return cluster
        if cluster and cluster.get("status") == "STATUS_FAILED":
            return cluster
        time.sleep(15)
    return cluster or {}


def main() -> None:
    """Module entrypoint."""
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        zone=dict(type="str"),
        vpc_id=dict(type="str"),
        version=dict(type="str"),
        public=dict(type="bool", default=False),
        pod_cidr_name=dict(type="str"),
        service_cidr_name=dict(type="str"),
        internal_lb_cidr_names=dict(type="list", elements="str"),
        oidc=dict(
            type="dict",
            options=dict(
                issuer_url=dict(type="str", required=True),
                client_id=dict(type="str", required=True),
                username_claim=dict(type="str"),
                username_prefix=dict(type="str"),
                groups_claim=dict(type="str"),
                groups_prefix=dict(type="str"),
                ca=dict(type="str", no_log=True),
            ),
        ),
        wait=dict(type="bool", default=True),
        wait_timeout=dict(type="int", default=2700),
        **REST_AUTH_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("zone", "vpc_id", "version", "pod_cidr_name", "service_cidr_name"), True),
        ],
    )

    api = CoreWeaveAPI(module)
    state = module.params["state"]
    name = module.params["name"]

    existing = find_cluster_by_name(api, name)

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, cluster={})
        if module.check_mode:
            module.exit_json(changed=True, cluster={})
        cluster_id = existing.get("id", existing.get("name"))
        try:
            api.delete(f"{CKS_BASE_PATH}/{cluster_id}")
        except CoreWeaveAPIError as e:
            module.fail_json(msg=f"Failed to delete cluster '{name}': {e.message}")
        module.exit_json(changed=True, cluster={})

    # state == present
    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True, cluster=build_create_payload(module.params))
        payload = build_create_payload(module.params)
        try:
            result = api.create(CKS_BASE_PATH, payload)
        except CoreWeaveAPIError as e:
            module.fail_json(msg=f"Failed to create cluster '{name}': {e.message}")

        if module.params["wait"]:
            cluster_id = result.get("id", result.get("name"))
            result = wait_for_status(api, cluster_id, "STATUS_RUNNING", module.params["wait_timeout"])
            if result.get("status") == "STATUS_FAILED":
                module.fail_json(msg=f"Cluster '{name}' entered FAILED state.", cluster=result)

        module.exit_json(changed=True, cluster=result)

    # Update existing
    update_payload = build_update_payload(module.params)
    if not update_payload:
        module.exit_json(changed=False, cluster=existing)

    if module.check_mode:
        module.exit_json(changed=True, cluster=existing)

    cluster_id = existing.get("id", existing.get("name"))
    try:
        result = api.update(f"{CKS_BASE_PATH}/{cluster_id}", update_payload)
    except CoreWeaveAPIError as e:
        module.fail_json(msg=f"Failed to update cluster '{name}': {e.message}")

    if module.params["wait"]:
        result = wait_for_status(api, cluster_id, "STATUS_RUNNING", module.params["wait_timeout"])

    module.exit_json(changed=True, cluster=result)


if __name__ == "__main__":
    main()
