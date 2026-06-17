#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_node_pool_info
short_description: Retrieve CoreWeave CKS Node Pool information
version_added: "0.2.0"
description:
  - Retrieve information about CKS Node Pool custom resources.
  - Can fetch a single Node Pool by name or list all Node Pools in a namespace.
  - Uses the C(compute.coreweave.com/v1alpha1) CRD API.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific Node Pool to retrieve.
      - If omitted, all Node Pools in the namespace are returned.
    type: str
  label_selector:
    description:
      - Kubernetes label selector to filter Node Pools.
    type: str
  field_selector:
    description:
      - Kubernetes field selector to filter Node Pools.
    type: str
extends_documentation_fragment:
  - stevefulme1.coreweave.auth
"""

EXAMPLES = r"""
- name: List all Node Pools
  stevefulme1.coreweave.coreweave_node_pool_info:
  register: all_pools

- name: Get a specific Node Pool
  stevefulme1.coreweave.coreweave_node_pool_info:
    name: a100-pool
  register: pool_info

- name: Display Node Pool status
  ansible.builtin.debug:
    msg: "Current nodes: {{ pool_info.node_pools[0].status.currentNodes }}"
"""

RETURN = r"""
node_pools:
  description: List of Node Pool resources.
  type: list
  elements: dict
  returned: always
  sample:
    - apiVersion: compute.coreweave.com/v1alpha1
      kind: NodePool
      metadata:
        name: a100-pool
      spec:
        instanceType: gd-8xa100-i128
        targetNodes: 4
      status:
        currentNodes: 4
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.stevefulme1.coreweave.plugins.module_utils.k8s_helper import (
    get_existing_resource,
    list_resources,
)

NP_API_VERSION = "compute.coreweave.com/v1alpha1"
NP_KIND = "NodePool"


def main():
    """Module entrypoint."""
    argument_spec = dict(
        name=dict(type="str"),
        namespace=dict(type="str", default="default"),
        kubeconfig=dict(type="path", aliases=["kubeconfig_path"]),
        context=dict(type="str"),
        label_selector=dict(type="str"),
        field_selector=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    namespace = module.params["namespace"]
    name = module.params.get("name")

    if name:
        existing = get_existing_resource(module, NP_API_VERSION, NP_KIND, name, namespace)
        if existing:
            module.exit_json(changed=False, node_pools=[existing])
        else:
            module.exit_json(changed=False, node_pools=[])
    else:
        items = list_resources(
            module,
            NP_API_VERSION,
            NP_KIND,
            namespace,
            label_selector=module.params.get("label_selector"),
            field_selector=module.params.get("field_selector"),
        )
        module.exit_json(changed=False, node_pools=items)


if __name__ == "__main__":
    main()
