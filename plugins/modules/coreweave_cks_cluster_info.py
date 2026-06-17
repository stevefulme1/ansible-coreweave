#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

DOCUMENTATION = r"""
---
module: coreweave_cks_cluster_info
short_description: Retrieve CoreWeave CKS cluster information
version_added: "0.2.0"
description:
  - Retrieve information about CoreWeave Kubernetes Service (CKS) clusters
    via the CoreWeave REST API.
  - Can fetch a single cluster by name or list all clusters.
  - Uses the C(/v1beta1/cks/clusters) API endpoint.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific cluster to retrieve.
      - If omitted, all clusters are returned.
    type: str
extends_documentation_fragment:
  - stevefulme1.coreweave.auth.REST
"""

EXAMPLES = r"""
- name: List all CKS clusters
  stevefulme1.coreweave.coreweave_cks_cluster_info:
    api_token: "{{ coreweave_token }}"
  register: all_clusters

- name: Get a specific cluster
  stevefulme1.coreweave.coreweave_cks_cluster_info:
    api_token: "{{ coreweave_token }}"
    name: ml-training-cluster
  register: cluster_info

- name: Display cluster status
  ansible.builtin.debug:
    msg: "Cluster status: {{ cluster_info.clusters[0].status }}"
"""

RETURN = r"""
clusters:
  description: List of CKS cluster resources.
  type: list
  elements: dict
  returned: always
  sample:
    - id: cluster-abc123
      name: ml-training-cluster
      zone: LAS1
      version: v1.32
      status: STATUS_RUNNING
      vpcId: vpc-abc123
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.coreweave_api import (
    REST_AUTH_ARGS,
    CoreWeaveAPI,
    CoreWeaveAPIError,
)

CKS_BASE_PATH = "/v1beta1/cks/clusters"


def main() -> None:
    """Module entrypoint."""
    argument_spec = dict(
        name=dict(type="str"),
        **REST_AUTH_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    api = CoreWeaveAPI(module)
    name = module.params.get("name")

    try:
        clusters = api.list(CKS_BASE_PATH)
    except CoreWeaveAPIError as e:
        module.fail_json(msg=f"Failed to list clusters: {e.message}")

    if name:
        clusters = [c for c in clusters if c.get("name") == name]

    module.exit_json(changed=False, clusters=clusters)


if __name__ == "__main__":
    main()
