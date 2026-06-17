#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

DOCUMENTATION = r"""
---
module: coreweave_node_pool
short_description: Manage CoreWeave CKS Node Pools
version_added: "0.2.0"
description:
  - Create, update, or delete CKS Node Pool custom resources.
  - Node Pools define groups of compute nodes with a specific instance type,
    scaling behavior, and configuration.
  - Uses the C(compute.coreweave.com/v1alpha1) CRD API.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the Node Pool resource.
    type: str
    required: true
  state:
    description:
      - Desired state of the Node Pool.
    type: str
    choices:
      - present
      - absent
    default: present
  instance_type:
    description:
      - Instance type for the nodes.
      - This field is immutable after creation.
      - Examples include C(gd-8xa100-i128), C(h100-80gb-sxm-ib).
    type: str
  target_nodes:
    description:
      - Desired number of nodes.
      - Mutually exclusive with C(target_racks).
    type: int
  target_racks:
    description:
      - Desired number of racks.
      - Only available for NVL72-powered instance types (GB200, GB300).
      - Mutually exclusive with C(target_nodes).
    type: int
  min_nodes:
    description:
      - Minimum nodes the autoscaler can scale down to.
    type: int
  max_nodes:
    description:
      - Maximum nodes the autoscaler can scale up to.
    type: int
  autoscaling:
    description:
      - Enable or disable cluster autoscaling.
    type: bool
    default: false
  compute_class:
    description:
      - Node Pool type.
    type: str
    choices:
      - default
    default: default
  scale_down_strategy:
    description:
      - Strategy for scaling down nodes.
      - C(IdleOnly) removes only idle nodes.
      - C(PreferIdle) removes idle nodes first, then active nodes.
    type: str
    choices:
      - IdleOnly
      - PreferIdle
    default: IdleOnly
  node_labels:
    description:
      - Labels to apply to nodes.
    type: dict
    default: {}
  node_annotations:
    description:
      - Annotations to apply to nodes.
    type: dict
    default: {}
  node_taints:
    description:
      - Taints to apply to nodes.
      - Each taint is a dict with C(key), C(value), and C(effect).
    type: list
    elements: dict
  gpu_driver_version:
    description:
      - GPU driver major version.
      - Mutually exclusive with C(image).
    type: str
  image:
    description:
      - Boot image configuration.
      - Mutually exclusive with C(gpu_driver_version).
    type: dict
    suboptions:
      name:
        description: Image name.
        type: str
      kernel:
        description: Kernel version.
        type: str
      release_train:
        description: Release channel.
        type: str
        choices:
          - stable
          - latest
        default: stable
  prefill:
    description:
      - Proactive node replacement configuration.
      - Requires C(autoscaling=false) and C(compute_class=default).
    type: dict
    suboptions:
      enabled:
        description: Enable prefill.
        type: bool
        default: false
      timeout:
        description: Max wait time for idle node (e.g., 24h).
        type: str
        default: "24h"
      max_nodes:
        description: Concurrent prefill replacement cap (1-4).
        type: int
        default: 3
extends_documentation_fragment:
  - stevefulme1.coreweave.auth
"""

EXAMPLES = r"""
- name: Create a GPU node pool
  stevefulme1.coreweave.coreweave_node_pool:
    name: a100-pool
    instance_type: gd-8xa100-i128
    target_nodes: 4
    min_nodes: 2
    max_nodes: 8
    autoscaling: true
    scale_down_strategy: PreferIdle
    node_labels:
      workload-type: training
    state: present

- name: Create a node pool with specific GPU driver
  stevefulme1.coreweave.coreweave_node_pool:
    name: inference-pool
    instance_type: h100-80gb-sxm-ib
    target_nodes: 2
    autoscaling: false
    gpu_driver_version: "550"
    state: present

- name: Delete a node pool
  stevefulme1.coreweave.coreweave_node_pool:
    name: a100-pool
    state: absent
"""

RETURN = r"""
result:
  description: The Node Pool resource state after the operation.
  type: dict
  returned: success
  sample:
    apiVersion: compute.coreweave.com/v1alpha1
    kind: NodePool
    metadata:
      name: a100-pool
    spec:
      instanceType: gd-8xa100-i128
      targetNodes: 4
      autoscaling: true
    status:
      currentNodes: 4
      conditions:
        - type: AtTarget
          reason: TargetMet
          status: "True"
changed:
  description: Whether the resource was changed.
  type: bool
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.stevefulme1.coreweave.plugins.module_utils.k8s_helper import (
    apply_resource,
)

NP_API_VERSION = "compute.coreweave.com/v1alpha1"
NP_KIND = "NodePool"


def build_manifest(params):
    """Build a NodePool CRD manifest from module parameters."""
    spec = {}

    if params.get("instance_type"):
        spec["instanceType"] = params["instance_type"]

    if params.get("compute_class"):
        spec["computeClass"] = params["compute_class"]

    if params.get("target_nodes") is not None:
        spec["targetNodes"] = params["target_nodes"]

    if params.get("target_racks") is not None:
        spec["targetRacks"] = params["target_racks"]

    if params.get("min_nodes") is not None:
        spec["minNodes"] = params["min_nodes"]

    if params.get("max_nodes") is not None:
        spec["maxNodes"] = params["max_nodes"]

    spec["autoscaling"] = params.get("autoscaling", False)

    if params.get("scale_down_strategy"):
        spec["lifecycle"] = {
            "scaleDownStrategy": params["scale_down_strategy"],
        }

    if params.get("node_labels"):
        spec["nodeLabels"] = params["node_labels"]

    if params.get("node_annotations"):
        spec["nodeAnnotations"] = params["node_annotations"]

    if params.get("node_taints"):
        spec["nodeTaints"] = params["node_taints"]

    if params.get("gpu_driver_version"):
        spec["gpu"] = {"version": params["gpu_driver_version"]}

    if params.get("image"):
        img = params["image"]
        image_spec = {}
        if img.get("name"):
            image_spec["name"] = img["name"]
        if img.get("kernel"):
            image_spec["kernel"] = img["kernel"]
        if img.get("release_train"):
            image_spec["releaseTrain"] = img["release_train"]
        if image_spec:
            spec["image"] = image_spec

    if params.get("prefill"):
        pf = params["prefill"]
        spec["prefill"] = {
            "enabled": pf.get("enabled", False),
        }
        if pf.get("timeout"):
            spec["prefill"]["timeout"] = pf["timeout"]
        if pf.get("max_nodes") is not None:
            spec["prefill"]["maxNodes"] = pf["max_nodes"]

    manifest = {
        "apiVersion": NP_API_VERSION,
        "kind": NP_KIND,
        "metadata": {
            "name": params["name"],
        },
        "spec": spec,
    }

    return manifest


def main():
    """Module entrypoint."""
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        namespace=dict(type="str", default="default"),
        kubeconfig=dict(type="path", aliases=["kubeconfig_path"]),
        context=dict(type="str"),
        instance_type=dict(type="str"),
        target_nodes=dict(type="int"),
        target_racks=dict(type="int"),
        min_nodes=dict(type="int"),
        max_nodes=dict(type="int"),
        autoscaling=dict(type="bool", default=False),
        compute_class=dict(type="str", choices=["default"], default="default"),
        scale_down_strategy=dict(type="str", choices=["IdleOnly", "PreferIdle"], default="IdleOnly"),
        node_labels=dict(type="dict", default={}),
        node_annotations=dict(type="dict", default={}),
        node_taints=dict(type="list", elements="dict"),
        gpu_driver_version=dict(type="str"),
        image=dict(
            type="dict",
            options=dict(
                name=dict(type="str"),
                kernel=dict(type="str"),
                release_train=dict(type="str", choices=["stable", "latest"], default="stable"),
            ),
        ),
        prefill=dict(
            type="dict",
            options=dict(
                enabled=dict(type="bool", default=False),
                timeout=dict(type="str", default="24h"),
                max_nodes=dict(type="int", default=3),
            ),
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ("target_nodes", "target_racks"),
            ("gpu_driver_version", "image"),
        ],
    )

    state = module.params["state"]
    namespace = module.params["namespace"]

    manifest = build_manifest(module.params)
    result = apply_resource(module, NP_API_VERSION, NP_KIND, manifest, namespace, state)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
