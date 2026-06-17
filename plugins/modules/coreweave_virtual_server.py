#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: coreweave_virtual_server
short_description: Manage CoreWeave VirtualServer instances
version_added: "3.0.0"
description:
  - Create, update, or delete CoreWeave VirtualServer custom resources.
  - VirtualServers are GPU-accelerated virtual machines running on CoreWeave's
    Kubernetes-native cloud platform.
  - This module builds a VirtualServer CRD manifest from user-friendly
    parameters and applies it using the Kubernetes API.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the VirtualServer resource.
    type: str
    required: true
  state:
    description:
      - Desired state of the VirtualServer.
      - C(present) ensures the VirtualServer exists with the specified configuration.
      - C(absent) ensures the VirtualServer is deleted.
    type: str
    choices:
      - present
      - absent
    default: present
  region:
    description:
      - CoreWeave datacenter region for deployment.
      - Common values include C(ORD1), C(LAS1), C(LGA1).
    type: str
    default: ORD1
  os_type:
    description:
      - Operating system type for the VirtualServer.
    type: str
    choices:
      - linux
      - windows
    default: linux
  gpu_type:
    description:
      - NVIDIA GPU type to attach to the VirtualServer.
      - Examples include C(Quadro_RTX_4000), C(RTX_A5000), C(A100_PCIE_40GB).
    type: str
  gpu_count:
    description:
      - Number of GPUs to attach.
    type: int
    default: 1
  cpu_count:
    description:
      - Number of CPU cores to allocate.
    type: int
    default: 4
  memory:
    description:
      - Amount of memory to allocate.
      - Accepts Kubernetes quantity strings such as C(16Gi), C(32Gi).
    type: str
    default: 16Gi
  root_disk_size:
    description:
      - Size of the root disk.
      - Accepts Kubernetes quantity strings such as C(40Gi), C(100Gi).
    type: str
    default: 40Gi
  storage_class_name:
    description:
      - Kubernetes StorageClass for the root disk.
      - Typically region-specific, such as C(block-nvme-ord1).
    type: str
  root_disk_source:
    description:
      - Source for the root disk DataVolume.
      - A dictionary with keys C(pvc) containing C(namespace) and C(name),
        or C(http) containing C(url).
    type: dict
  users:
    description:
      - List of user accounts to create on the VirtualServer.
      - Each entry is a dictionary with C(username) and optionally
        C(password) or C(sshpublickey).
    type: list
    elements: dict
  network_public:
    description:
      - Whether to assign a public IP address.
    type: bool
    default: true
  tcp_ports:
    description:
      - List of TCP ports to expose.
    type: list
    elements: int
    default:
      - 22
  udp_ports:
    description:
      - List of UDP ports to expose.
    type: list
    elements: int
  cloud_init:
    description:
      - Cloud-init user data for the VirtualServer.
    type: str
  initialize_running:
    description:
      - Whether the VirtualServer should start immediately after creation.
    type: bool
    default: true
  labels:
    description:
      - Dictionary of labels to apply to the VirtualServer metadata.
    type: dict
    default: {}
  annotations:
    description:
      - Dictionary of annotations to apply to the VirtualServer metadata.
    type: dict
    default: {}
extends_documentation_fragment:
  - stevefulme1.coreweave.auth
"""

EXAMPLES = r"""
- name: Create a Linux VirtualServer with GPU
  stevefulme1.coreweave.coreweave_virtual_server:
    name: my-gpu-workstation
    region: ORD1
    os_type: linux
    gpu_type: Quadro_RTX_4000
    gpu_count: 1
    cpu_count: 4
    memory: 16Gi
    root_disk_size: 40Gi
    storage_class_name: block-nvme-ord1
    root_disk_source:
      pvc:
        namespace: vd-images
        name: ubuntu2004-nvidia-510-47-03-1-docker-master-20220421-ord1
    users:
      - username: admin
        password: changeme
    tcp_ports:
      - 22
      - 8080
    state: present

- name: Create a CPU-only VirtualServer
  stevefulme1.coreweave.coreweave_virtual_server:
    name: cpu-worker
    region: LAS1
    os_type: linux
    cpu_count: 8
    memory: 32Gi
    root_disk_size: 100Gi
    storage_class_name: block-nvme-las1
    root_disk_source:
      http:
        url: https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img
    state: present

- name: Delete a VirtualServer
  stevefulme1.coreweave.coreweave_virtual_server:
    name: my-gpu-workstation
    state: absent
"""

RETURN = r"""
result:
  description: The VirtualServer resource state after the operation.
  type: dict
  returned: success
  sample:
    apiVersion: virtualservers.coreweave.com/v1alpha1
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
changed:
  description: Whether the resource was changed.
  type: bool
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.k8s_helper import (
    apply_resource,
)

VS_API_VERSION = "virtualservers.coreweave.com/v1alpha1"
VS_KIND = "VirtualServer"


def build_manifest(params):
    """Build a VirtualServer CRD manifest from module parameters.

    Args:
        params: Module parameters dict.

    Returns:
        dict: Kubernetes VirtualServer manifest.
    """
    spec = {
        "region": params["region"],
        "os": {"type": params["os_type"]},
        "resources": {
            "cpu": {"count": params["cpu_count"]},
            "memory": params["memory"],
        },
        "storage": {
            "root": {
                "size": params["root_disk_size"],
            },
        },
        "network": {
            "public": params["network_public"],
        },
        "initializeRunning": params["initialize_running"],
    }

    # GPU configuration
    if params.get("gpu_type"):
        spec["resources"]["gpu"] = {
            "type": params["gpu_type"],
            "count": params["gpu_count"],
        }

    # Storage class
    if params.get("storage_class_name"):
        spec["storage"]["root"]["storageClassName"] = params["storage_class_name"]

    # Root disk source
    if params.get("root_disk_source"):
        spec["storage"]["root"]["source"] = params["root_disk_source"]

    # Users
    if params.get("users"):
        spec["users"] = params["users"]

    # TCP ports
    if params.get("tcp_ports"):
        spec["network"]["tcp"] = {"ports": params["tcp_ports"]}

    # UDP ports
    if params.get("udp_ports"):
        spec["network"]["udp"] = {"ports": params["udp_ports"]}

    # Cloud-init
    if params.get("cloud_init"):
        spec["cloudInit"] = params["cloud_init"]

    manifest = {
        "apiVersion": VS_API_VERSION,
        "kind": VS_KIND,
        "metadata": {
            "name": params["name"],
        },
        "spec": spec,
    }

    # Labels and annotations
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
        region=dict(type="str", default="ORD1"),
        os_type=dict(type="str", choices=["linux", "windows"], default="linux"),
        gpu_type=dict(type="str"),
        gpu_count=dict(type="int", default=1),
        cpu_count=dict(type="int", default=4),
        memory=dict(type="str", default="16Gi"),
        root_disk_size=dict(type="str", default="40Gi"),
        storage_class_name=dict(type="str"),
        root_disk_source=dict(type="dict"),
        users=dict(type="list", elements="dict", no_log=False),
        network_public=dict(type="bool", default=True),
        tcp_ports=dict(type="list", elements="int", default=[22]),
        udp_ports=dict(type="list", elements="int"),
        cloud_init=dict(type="str"),
        initialize_running=dict(type="bool", default=True),
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
    result = apply_resource(module, VS_API_VERSION, VS_KIND, manifest, namespace, state)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
