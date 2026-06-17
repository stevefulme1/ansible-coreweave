# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

DOCUMENTATION = r"""
---
name: coreweave
short_description: CoreWeave CKS dynamic inventory
version_added: "0.2.0"
description:
  - Dynamically builds inventory from CoreWeave CKS cluster nodes.
  - Queries CKS clusters via the REST API, then enumerates nodes via the
    Kubernetes API for each cluster.
  - Groups hosts by GPU type, region, node pool, and instance type.
author:
  - Steve Fulmer (@stevefulme1)
options:
  plugin:
    description: Token that ensures this is a source file for the plugin.
    required: true
    choices:
      - stevefulme1.coreweave.coreweave
  api_token:
    description:
      - CoreWeave API access token.
      - Can be set via the E(COREWEAVE_API_TOKEN) environment variable.
    type: str
    required: true
    env:
      - name: COREWEAVE_API_TOKEN
  api_url:
    description:
      - CoreWeave API base URL.
    type: str
    default: https://api.coreweave.com
    env:
      - name: COREWEAVE_API_URL
  clusters:
    description:
      - List of cluster names to include.
      - If omitted, all clusters are included.
    type: list
    elements: str
  kubeconfig:
    description:
      - Path to kubeconfig file for K8s node enumeration.
      - If not provided, uses default kubeconfig location.
    type: path
    env:
      - name: KUBECONFIG
  compose:
    description:
      - Dictionary of Jinja2 expressions to create host variables.
    type: dict
    default: {}
  groups:
    description:
      - Dictionary of group definitions using Jinja2 conditionals.
    type: dict
    default: {}
  keyed_groups:
    description:
      - List of keyed group definitions.
    type: list
    elements: dict
    default: []
requirements:
  - kubernetes >= 28.1.0
  - python >= 3.12
"""

EXAMPLES = r"""
# coreweave.yml inventory file
---
plugin: stevefulme1.coreweave.coreweave
api_token: "{{ lookup('env', 'COREWEAVE_API_TOKEN') }}"

# Only include specific clusters
---
plugin: stevefulme1.coreweave.coreweave
api_token: "{{ lookup('env', 'COREWEAVE_API_TOKEN') }}"
clusters:
  - ml-training-cluster
  - inference-cluster

# With keyed groups
---
plugin: stevefulme1.coreweave.coreweave
api_token: "{{ lookup('env', 'COREWEAVE_API_TOKEN') }}"
keyed_groups:
  - key: gpu_type
    prefix: gpu
  - key: region
    prefix: region
  - key: node_pool
    prefix: pool
"""

import json

from ansible.errors import AnsibleError
from ansible.module_utils.urls import open_url
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable

try:
    from kubernetes import client, config
    HAS_K8S = True
except ImportError:
    HAS_K8S = False


class InventoryModule(BaseInventoryPlugin, Constructable):
    """CoreWeave CKS dynamic inventory plugin."""

    NAME = "stevefulme1.coreweave.coreweave"

    def verify_file(self, path):
        """Verify the inventory source file."""
        if super().verify_file(path):
            return path.endswith((".coreweave.yml", ".coreweave.yaml"))
        return False

    def _get_clusters(self, api_url, api_token):
        """Fetch CKS clusters from the REST API."""
        url = f"{api_url}/v1beta1/cks/clusters"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
        }
        try:
            response = open_url(url, headers=headers, method="GET", validate_certs=True)
            data = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            raise AnsibleError(f"Failed to fetch CKS clusters: {e}") from e

        if isinstance(data, list):
            return data
        for key in ("clusters", "items", "data"):
            if key in data:
                return data[key]
        return [data]

    def _get_k8s_nodes(self, kubeconfig, context=None):
        """Fetch nodes from a Kubernetes cluster."""
        if not HAS_K8S:
            self.display.warning("kubernetes Python library not installed — skipping node enumeration")
            return []

        try:
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig, context=context)
            else:
                try:
                    config.load_incluster_config()
                except config.ConfigException:
                    config.load_kube_config(context=context)
        except Exception as e:
            self.display.warning(f"Failed to load kubeconfig: {e}")
            return []

        v1 = client.CoreV1Api()
        try:
            nodes = v1.list_node()
            return [node.to_dict() for node in nodes.items]
        except Exception as e:
            self.display.warning(f"Failed to list nodes: {e}")
            return []

    def parse(self, inventory, loader, path, cache=True):
        """Parse the inventory source."""
        super().parse(inventory, loader, path, cache)
        self._read_config_data(path)

        api_token = self.get_option("api_token")
        api_url = self.get_option("api_url")
        cluster_filter = self.get_option("clusters")
        kubeconfig = self.get_option("kubeconfig")

        if not api_token:
            raise AnsibleError("api_token is required")

        clusters = self._get_clusters(api_url, api_token)

        if cluster_filter:
            clusters = [c for c in clusters if c.get("name") in cluster_filter]

        for cluster_data in clusters:
            cluster_name = cluster_data.get("name", "unknown")
            cluster_zone = cluster_data.get("zone", "unknown")
            cluster_status = cluster_data.get("status", "unknown")

            group_name = self.inventory.add_group(f"cluster_{cluster_name}")
            self.inventory.set_variable(group_name, "cluster_zone", cluster_zone)
            self.inventory.set_variable(group_name, "cluster_status", cluster_status)

            zone_group = self.inventory.add_group(f"zone_{cluster_zone}")

            nodes = self._get_k8s_nodes(kubeconfig, context=cluster_name)

            for node in nodes:
                node_name = node.get("metadata", {}).get("name", "unknown")
                labels = node.get("metadata", {}).get("labels", {})

                self.inventory.add_host(node_name, group=group_name)
                self.inventory.add_host(node_name, group=zone_group)

                addresses = node.get("status", {}).get("addresses", [])
                for addr in addresses:
                    if addr.get("type") == "InternalIP":
                        self.inventory.set_variable(node_name, "ansible_host", addr["address"])
                        break

                self.inventory.set_variable(node_name, "cluster_name", cluster_name)
                self.inventory.set_variable(node_name, "region", cluster_zone)
                self.inventory.set_variable(node_name, "node_labels", labels)

                instance_type = labels.get("node.kubernetes.io/instance-type", "unknown")
                self.inventory.set_variable(node_name, "instance_type", instance_type)

                gpu_type = labels.get("gpu.nvidia.com/class", labels.get("nvidia.com/gpu.product", "none"))
                self.inventory.set_variable(node_name, "gpu_type", gpu_type)

                node_pool = labels.get("topology.coreweave.cloud/node-pool", "unknown")
                self.inventory.set_variable(node_name, "node_pool", node_pool)

                if gpu_type != "none":
                    gpu_group = self.inventory.add_group(f"gpu_{gpu_type}")
                    self.inventory.add_host(node_name, group=gpu_group)

                if node_pool != "unknown":
                    pool_group = self.inventory.add_group(f"pool_{node_pool}")
                    self.inventory.add_host(node_name, group=pool_group)

                it_group = self.inventory.add_group(f"instance_{instance_type}")
                self.inventory.add_host(node_name, group=it_group)

                self._set_composite_vars(
                    self.get_option("compose"),
                    self.inventory.get_host(node_name).get_vars(),
                    node_name,
                    strict=False,
                )
                self._add_host_to_composed_groups(
                    self.get_option("groups"),
                    self.inventory.get_host(node_name).get_vars(),
                    node_name,
                    strict=False,
                )
                self._add_host_to_keyed_groups(
                    self.get_option("keyed_groups"),
                    self.inventory.get_host(node_name).get_vars(),
                    node_name,
                    strict=False,
                )

            if not nodes:
                self.inventory.add_host(cluster_name, group=group_name)
                self.inventory.set_variable(cluster_name, "ansible_host", cluster_name)
                self.inventory.set_variable(cluster_name, "cluster_name", cluster_name)
                self.inventory.set_variable(cluster_name, "region", cluster_zone)
                self.inventory.set_variable(cluster_name, "cluster_status", cluster_status)
                self.inventory.set_variable(cluster_name, "gpu_type", "none")
                self.inventory.set_variable(cluster_name, "node_pool", "none")
                self.inventory.set_variable(cluster_name, "instance_type", "none")
