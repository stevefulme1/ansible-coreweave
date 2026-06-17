#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, annotations, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: coreweave_inference_service_info
short_description: Retrieve CoreWeave InferenceService information
version_added: "3.0.0"
description:
  - Retrieve information about KServe InferenceService resources on CoreWeave.
  - Can fetch a single InferenceService by name or list all InferenceServices
    in a namespace.
  - Returns InferenceService metadata, spec, and status including URL,
    readiness, and traffic information.
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific InferenceService to retrieve.
      - If omitted, all InferenceServices in the namespace are returned.
    type: str
  label_selector:
    description:
      - Kubernetes label selector to filter InferenceServices.
    type: str
  field_selector:
    description:
      - Kubernetes field selector to filter InferenceServices.
    type: str
extends_documentation_fragment:
  - stevefulme1.coreweave.auth
"""

EXAMPLES = r"""
- name: Get a specific InferenceService
  stevefulme1.coreweave.coreweave_inference_service_info:
    name: sentiment-analyzer
  register: isvc_info

- name: List all InferenceServices
  stevefulme1.coreweave.coreweave_inference_service_info:
    namespace: ml-serving
  register: all_isvcs

- name: List InferenceServices with label selector
  stevefulme1.coreweave.coreweave_inference_service_info:
    label_selector: "qos.coreweave.cloud/latency=low"
  register: low_latency_isvcs

- name: Display InferenceService URL
  ansible.builtin.debug:
    msg: "URL: {{ isvc_info.inference_services[0].status.url }}"
"""

RETURN = r"""
inference_services:
  description: List of InferenceService resources.
  type: list
  elements: dict
  returned: always
  sample:
    - apiVersion: serving.kubeflow.org/v1beta1
      kind: InferenceService
      metadata:
        name: sentiment-analyzer
        namespace: default
      spec:
        predictor:
          minReplicas: 0
          maxReplicas: 10
      status:
        url: http://sentiment-analyzer.default.example.com
        conditions:
          - type: Ready
            status: "True"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.coreweave.plugins.module_utils.k8s_helper import (
    get_existing_resource,
    list_resources,
)

ISVC_API_VERSION = "serving.kubeflow.org/v1beta1"
ISVC_KIND = "InferenceService"


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
        existing = get_existing_resource(module, ISVC_API_VERSION, ISVC_KIND, name, namespace)
        if existing:
            module.exit_json(changed=False, inference_services=[existing])
        else:
            module.exit_json(changed=False, inference_services=[])
    else:
        items = list_resources(
            module,
            ISVC_API_VERSION,
            ISVC_KIND,
            namespace,
            label_selector=module.params.get("label_selector"),
            field_selector=module.params.get("field_selector"),
        )
        module.exit_json(changed=False, inference_services=items)


if __name__ == "__main__":
    main()
