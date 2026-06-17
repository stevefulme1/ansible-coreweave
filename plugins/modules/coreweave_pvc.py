#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: coreweave_pvc
short_description: Manage PersistentVolumeClaims on CoreWeave
version_added: "3.0.0"
description:
  - Create, update, or delete Kubernetes PersistentVolumeClaim resources
    on CoreWeave clusters.
  - Provides user-friendly parameters for CoreWeave-specific storage classes
    and volume modes.
  - Commonly used to provision shared storage for model weights, datasets,
    and VirtualServer disks.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the PersistentVolumeClaim.
    type: str
    required: true
  state:
    description:
      - Desired state of the PVC.
    type: str
    choices:
      - present
      - absent
    default: present
  storage_size:
    description:
      - Requested storage size.
      - Accepts Kubernetes quantity strings such as C(10Gi), C(100Gi), C(1Ti).
    type: str
    default: 10Gi
  storage_class_name:
    description:
      - Kubernetes StorageClass name.
      - CoreWeave provides classes such as C(shared-hdd-ord1), C(shared-nvme-ord1),
        C(block-nvme-ord1), and C(block-hdd-ord1).
    type: str
  access_modes:
    description:
      - List of access modes for the PVC.
      - Common values are C(ReadWriteOnce), C(ReadWriteMany), C(ReadOnlyMany).
    type: list
    elements: str
    default:
      - ReadWriteOnce
  volume_mode:
    description:
      - Volume mode for the PVC.
      - Use C(Filesystem) for shared storage and C(Block) for raw block devices.
    type: str
    choices:
      - Filesystem
      - Block
    default: Filesystem
  labels:
    description:
      - Dictionary of labels to apply to the PVC metadata.
    type: dict
    default: {}
  annotations:
    description:
      - Dictionary of annotations to apply to the PVC metadata.
    type: dict
    default: {}
extends_documentation_fragment:
  - stevefulme1.coreweave.auth
"""

EXAMPLES = r"""
- name: Create a shared storage PVC for model weights
  stevefulme1.coreweave.coreweave_pvc:
    name: model-storage
    storage_size: 100Gi
    storage_class_name: shared-hdd-ord1
    access_modes:
      - ReadWriteMany
    volume_mode: Filesystem
    state: present

- name: Create a block storage PVC
  stevefulme1.coreweave.coreweave_pvc:
    name: vm-disk
    storage_size: 40Gi
    storage_class_name: block-nvme-ord1
    access_modes:
      - ReadWriteOnce
    volume_mode: Block
    state: present

- name: Delete a PVC
  stevefulme1.coreweave.coreweave_pvc:
    name: model-storage
    state: absent
"""

RETURN = r"""
result:
  description: The PVC resource state after the operation.
  type: dict
  returned: success
  sample:
    apiVersion: v1
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
      volumeMode: Filesystem
changed:
  description: Whether the resource was changed.
  type: bool
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.k8s_helper import (
    apply_resource,
)

PVC_API_VERSION = "v1"
PVC_KIND = "PersistentVolumeClaim"


def build_manifest(params):
    """Build a PVC manifest from module parameters.

    Args:
        params: Module parameters dict.

    Returns:
        dict: Kubernetes PVC manifest.
    """
    spec = {
        "accessModes": params["access_modes"],
        "resources": {
            "requests": {
                "storage": params["storage_size"],
            },
        },
        "volumeMode": params["volume_mode"],
    }

    if params.get("storage_class_name"):
        spec["storageClassName"] = params["storage_class_name"]

    manifest = {
        "apiVersion": PVC_API_VERSION,
        "kind": PVC_KIND,
        "metadata": {
            "name": params["name"],
        },
        "spec": spec,
    }

    if params.get("labels"):
        manifest["metadata"]["labels"] = params["labels"]
    if params.get("annotations"):
        manifest["metadata"]["annotations"] = params["annotations"]

    return manifest


def main():
    """Module entrypoint."""
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        namespace=dict(type="str", default="default"),
        kubeconfig=dict(type="path", aliases=["kubeconfig_path"]),
        context=dict(type="str"),
        storage_size=dict(type="str", default="10Gi"),
        storage_class_name=dict(type="str"),
        access_modes=dict(type="list", elements="str", default=["ReadWriteOnce"]),
        volume_mode=dict(type="str", choices=["Filesystem", "Block"], default="Filesystem"),
        labels=dict(type="dict", default={}),
        annotations=dict(type="dict", default={}),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    state = module.params["state"]
    namespace = module.params["namespace"]

    manifest = build_manifest(module.params)
    result = apply_resource(module, PVC_API_VERSION, PVC_KIND, manifest, namespace, state)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
