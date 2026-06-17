#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type


DOCUMENTATION = r"""
---
module: coreweave_pvc_info
short_description: Retrieve PersistentVolumeClaim information on CoreWeave
version_added: "3.0.0"
description:
  - Retrieve information about Kubernetes PersistentVolumeClaim resources
    on CoreWeave clusters.
  - Can fetch a single PVC by name or list all PVCs in a namespace.
  - Returns PVC metadata, spec, and status including phase, capacity,
    and access modes.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific PVC to retrieve.
      - If omitted, all PVCs in the namespace are returned.
    type: str
  label_selector:
    description:
      - Kubernetes label selector to filter PVCs.
    type: str
  field_selector:
    description:
      - Kubernetes field selector to filter PVCs.
    type: str
extends_documentation_fragment:
  - stevefulme1.coreweave.auth
"""

EXAMPLES = r"""
- name: Get a specific PVC
  stevefulme1.coreweave.coreweave_pvc_info:
    name: model-storage
  register: pvc_info

- name: List all PVCs in namespace
  stevefulme1.coreweave.coreweave_pvc_info:
    namespace: ml-serving
  register: all_pvcs

- name: List PVCs with label selector
  stevefulme1.coreweave.coreweave_pvc_info:
    label_selector: "app=ml-training"
  register: filtered_pvcs

- name: Display PVC capacity
  ansible.builtin.debug:
    msg: "Capacity: {{ pvc_info.pvcs[0].status.capacity.storage }}"
"""

RETURN = r"""
pvcs:
  description: List of PersistentVolumeClaim resources.
  type: list
  elements: dict
  returned: always
  sample:
    - apiVersion: v1
      kind: PersistentVolumeClaim
      metadata:
        name: model-storage
        namespace: default
      spec:
        accessModes:
          - ReadWriteMany
        resources:
          requests:
            storage: 100Gi
        storageClassName: shared-hdd-ord1
      status:
        phase: Bound
        capacity:
          storage: 100Gi
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.k8s_helper import (
    get_existing_resource,
    list_resources,
)

PVC_API_VERSION = "v1"
PVC_KIND = "PersistentVolumeClaim"


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
        existing = get_existing_resource(module, PVC_API_VERSION, PVC_KIND, name, namespace)
        if existing:
            module.exit_json(changed=False, pvcs=[existing])
        else:
            module.exit_json(changed=False, pvcs=[])
    else:
        items = list_resources(
            module,
            PVC_API_VERSION,
            PVC_KIND,
            namespace,
            label_selector=module.params.get("label_selector"),
            field_selector=module.params.get("field_selector"),
        )
        module.exit_json(changed=False, pvcs=items)


if __name__ == "__main__":
    main()
