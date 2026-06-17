#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)



DOCUMENTATION = r"""
---
module: coreweave_virtual_server_info
short_description: Retrieve CoreWeave VirtualServer information
version_added: "3.0.0"
description:
  - Retrieve information about CoreWeave VirtualServer custom resources.
  - Can fetch a single VirtualServer by name or list all VirtualServers
    in a namespace.
  - Returns VirtualServer metadata, spec, and status including network
    information and readiness conditions.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific VirtualServer to retrieve.
      - If omitted, all VirtualServers in the namespace are returned.
    type: str
  label_selector:
    description:
      - Kubernetes label selector to filter VirtualServers.
      - Uses standard Kubernetes label selector syntax.
    type: str
  field_selector:
    description:
      - Kubernetes field selector to filter VirtualServers.
    type: str
extends_documentation_fragment:
  - stevefulme1.coreweave.auth
"""

EXAMPLES = r"""
- name: Get a specific VirtualServer
  stevefulme1.coreweave.coreweave_virtual_server_info:
    name: my-gpu-workstation
  register: vs_info

- name: List all VirtualServers in namespace
  stevefulme1.coreweave.coreweave_virtual_server_info:
    namespace: my-project
  register: all_vs

- name: List VirtualServers with label selector
  stevefulme1.coreweave.coreweave_virtual_server_info:
    label_selector: "app=ml-training"
  register: filtered_vs

- name: Display VirtualServer network info
  ansible.builtin.debug:
    msg: "IP: {{ vs_info.virtual_servers[0].status.network.externalIP }}"
"""

RETURN = r"""
virtual_servers:
  description: List of VirtualServer resources.
  type: list
  elements: dict
  returned: always
  sample:
    - apiVersion: virtualservers.coreweave.com/v1alpha1
      kind: VirtualServer
      metadata:
        name: my-gpu-workstation
        namespace: default
      spec:
        region: ORD1
        os:
          type: linux
        resources:
          gpu:
            type: Quadro_RTX_4000
            count: 1
          cpu:
            count: 4
          memory: 16Gi
      status:
        conditions:
          - type: VirtualMachineReady
            status: "True"
        network:
          externalIP: 216.153.x.x
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.k8s_helper import (
    get_existing_resource,
    list_resources,
)

VS_API_VERSION = "virtualservers.coreweave.com/v1alpha1"
VS_KIND = "VirtualServer"


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
        existing = get_existing_resource(module, VS_API_VERSION, VS_KIND, name, namespace)
        if existing:
            module.exit_json(changed=False, virtual_servers=[existing])
        else:
            module.exit_json(changed=False, virtual_servers=[])
    else:
        items = list_resources(
            module,
            VS_API_VERSION,
            VS_KIND,
            namespace,
            label_selector=module.params.get("label_selector"),
            field_selector=module.params.get("field_selector"),
        )
        module.exit_json(changed=False, virtual_servers=items)


if __name__ == "__main__":
    main()
