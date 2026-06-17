#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: coreweave_inference_service
short_description: Manage CoreWeave InferenceService resources
version_added: "3.0.0"
description:
  - Create, update, or delete InferenceService resources on CoreWeave.
  - Supports KServe C(serving.kubeflow.org/v1beta1) InferenceService for
    deploying ML models with autoscaling, scale-to-zero, and GPU scheduling.
  - Builds the correct CRD manifest from user-friendly parameters and
    applies it using the Kubernetes API.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the InferenceService resource.
    type: str
    required: true
  state:
    description:
      - Desired state of the InferenceService.
    type: str
    choices:
      - present
      - absent
    default: present
  runtime:
    description:
      - Serving runtime framework for the predictor container.
      - Use C(custom) to provide a full container spec via I(container_image).
    type: str
    choices:
      - custom
      - tensorflow
      - pytorch
      - sklearn
      - xgboost
    default: custom
  container_image:
    description:
      - Container image for the predictor.
      - Required when I(runtime=custom).
    type: str
  container_command:
    description:
      - Command to run in the predictor container.
    type: list
    elements: str
  container_args:
    description:
      - Arguments for the predictor container command.
    type: list
    elements: str
  container_env:
    description:
      - Environment variables for the predictor container.
      - List of dicts with C(name) and C(value) or C(valueFrom) keys.
    type: list
    elements: dict
  container_port:
    description:
      - Port the predictor container listens on.
    type: int
    default: 80
  storage_uri:
    description:
      - URI pointing to the model storage location.
      - Supports C(pvc://), C(s3://), C(gs://), and C(http://) schemes.
    type: str
  gpu_type:
    description:
      - NVIDIA GPU class for node affinity scheduling.
      - Examples include C(Quadro_RTX_5000), C(A100_PCIE_40GB), C(RTX_A5000).
    type: str
  gpu_count:
    description:
      - Number of GPUs to request per replica.
    type: int
    default: 1
  cpu_request:
    description:
      - CPU request per replica.
    type: str
    default: "1"
  cpu_limit:
    description:
      - CPU limit per replica.
    type: str
  memory_request:
    description:
      - Memory request per replica.
    type: str
    default: 8Gi
  memory_limit:
    description:
      - Memory limit per replica.
    type: str
  min_replicas:
    description:
      - Minimum number of replicas.
      - Set to C(0) to enable scale-to-zero.
    type: int
    default: 0
  max_replicas:
    description:
      - Maximum number of replicas for autoscaling.
    type: int
    default: 10
  container_concurrency:
    description:
      - Maximum number of concurrent requests per replica.
    type: int
    default: 1
  region:
    description:
      - CoreWeave region for node affinity.
    type: str
  labels:
    description:
      - Dictionary of labels to apply to the InferenceService metadata.
    type: dict
    default: {}
  annotations:
    description:
      - Dictionary of annotations to apply to the InferenceService metadata.
    type: dict
    default: {}
extends_documentation_fragment:
  - stevefulme1.coreweave.auth
"""

EXAMPLES = r"""
- name: Deploy a custom inference service
  stevefulme1.coreweave.coreweave_inference_service:
    name: sentiment-analyzer
    runtime: custom
    container_image: coreweave/fastai-sentiment:4
    container_env:
      - name: STORAGE_URI
        value: pvc://model-storage/sentiment
    gpu_type: Quadro_RTX_5000
    gpu_count: 1
    cpu_request: "1"
    cpu_limit: "3"
    memory_request: 6Gi
    memory_limit: 8Gi
    min_replicas: 0
    max_replicas: 10
    container_concurrency: 1
    labels:
      qos.coreweave.cloud/latency: low
    state: present

- name: Deploy a TensorFlow model
  stevefulme1.coreweave.coreweave_inference_service:
    name: image-classifier
    runtime: tensorflow
    storage_uri: pvc://model-storage/inception
    gpu_type: RTX_A5000
    min_replicas: 1
    max_replicas: 5
    state: present

- name: Delete an inference service
  stevefulme1.coreweave.coreweave_inference_service:
    name: sentiment-analyzer
    state: absent
"""

RETURN = r"""
result:
  description: The InferenceService resource state after the operation.
  type: dict
  returned: success
  sample:
    apiVersion: serving.kubeflow.org/v1beta1
    kind: InferenceService
    metadata:
      name: sentiment-analyzer
      namespace: default
    spec:
      predictor:
        minReplicas: 0
        maxReplicas: 10
        containerConcurrency: 1
changed:
  description: Whether the resource was changed.
  type: bool
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.k8s_helper import (
    apply_resource,
)

ISVC_API_VERSION = "serving.kubeflow.org/v1beta1"
ISVC_KIND = "InferenceService"


def build_manifest(params):
    """Build an InferenceService CRD manifest from module parameters.

    Args:
        params: Module parameters dict.

    Returns:
        dict: Kubernetes InferenceService manifest.
    """
    # Build resource requests and limits
    resources = {
        "requests": {
            "cpu": params["cpu_request"],
            "memory": params["memory_request"],
        },
        "limits": {},
    }

    if params.get("gpu_type"):
        resources["requests"]["nvidia.com/gpu"] = str(params["gpu_count"])
        resources["limits"]["nvidia.com/gpu"] = str(params["gpu_count"])

    if params.get("cpu_limit"):
        resources["limits"]["cpu"] = params["cpu_limit"]
    if params.get("memory_limit"):
        resources["limits"]["memory"] = params["memory_limit"]

    # Clean up empty limits
    if not resources["limits"]:
        del resources["limits"]

    predictor = {
        "minReplicas": params["min_replicas"],
        "maxReplicas": params["max_replicas"],
        "containerConcurrency": params["container_concurrency"],
    }

    runtime = params["runtime"]

    if runtime == "custom":
        container = {
            "name": "kfserving-container",
            "resources": resources,
        }
        if params.get("container_image"):
            container["image"] = params["container_image"]
        if params.get("container_command"):
            container["command"] = params["container_command"]
        if params.get("container_args"):
            container["args"] = params["container_args"]
        if params.get("container_env"):
            container["env"] = params["container_env"]
        container["ports"] = [{"protocol": "TCP", "containerPort": params["container_port"]}]

        predictor["containers"] = [container]
    else:
        # KServe built-in runtimes (tensorflow, pytorch, sklearn, xgboost)
        runtime_spec = {"resources": resources}
        if params.get("storage_uri"):
            runtime_spec["storageUri"] = params["storage_uri"]
        predictor[runtime] = runtime_spec

    # GPU node affinity
    if params.get("gpu_type"):
        match_expressions = [
            {
                "key": "gpu.nvidia.com/class",
                "operator": "In",
                "values": [params["gpu_type"]],
            }
        ]
        if params.get("region"):
            match_expressions.append(
                {
                    "key": "topology.kubernetes.io/region",
                    "operator": "In",
                    "values": [params["region"]],
                }
            )
        predictor["affinity"] = {
            "nodeAffinity": {
                "requiredDuringSchedulingIgnoredDuringExecution": {
                    "nodeSelectorTerms": [{"matchExpressions": match_expressions}]
                }
            }
        }

    manifest = {
        "apiVersion": ISVC_API_VERSION,
        "kind": ISVC_KIND,
        "metadata": {
            "name": params["name"],
        },
        "spec": {
            "predictor": predictor,
        },
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
        runtime=dict(type="str", choices=["custom", "tensorflow", "pytorch", "sklearn", "xgboost"], default="custom"),
        container_image=dict(type="str"),
        container_command=dict(type="list", elements="str"),
        container_args=dict(type="list", elements="str"),
        container_env=dict(type="list", elements="dict"),
        container_port=dict(type="int", default=80),
        storage_uri=dict(type="str"),
        gpu_type=dict(type="str"),
        gpu_count=dict(type="int", default=1),
        cpu_request=dict(type="str", default="1"),
        cpu_limit=dict(type="str"),
        memory_request=dict(type="str", default="8Gi"),
        memory_limit=dict(type="str"),
        min_replicas=dict(type="int", default=0),
        max_replicas=dict(type="int", default=10),
        container_concurrency=dict(type="int", default=1),
        region=dict(type="str"),
        labels=dict(type="dict", default={}),
        annotations=dict(type="dict", default={}),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("runtime", "custom", ("container_image",)),
        ],
    )

    state = module.params["state"]
    namespace = module.params["namespace"]

    manifest = build_manifest(module.params)
    result = apply_resource(module, ISVC_API_VERSION, ISVC_KIND, manifest, namespace, state)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
