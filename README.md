# Ansible Collection - stevefulme1.coreweave

Ansible collection for managing CoreWeave cloud infrastructure via the
CoreWeave REST API and Kubernetes-native CRDs.

## Overview

CoreWeave is a Kubernetes-native GPU cloud platform. This collection provides:

- **REST API modules** for CKS clusters, VPCs, and Object Storage
- **K8s CRD modules** for VirtualServers, InferenceServices, Node Pools, and PVCs
- **Dynamic inventory** from CKS clusters grouped by GPU type, region, and node pool
- **EDA event source plugins** for webhook alerts and K8s event watching

## Modules

### REST API Modules (api.coreweave.com)

| Module | API Endpoint | Description |
|--------|-------------|-------------|
| `coreweave_cks_cluster` | `/v1beta1/cks/clusters` | Manage CKS clusters |
| `coreweave_cks_cluster_info` | `/v1beta1/cks/clusters` | List/get CKS clusters |
| `coreweave_vpc` | `/v1beta1/networking/vpcs` | Manage VPCs |
| `coreweave_vpc_info` | `/v1beta1/networking/vpcs` | List/get VPCs |
| `coreweave_object_storage_key` | `/v1/cwobject/access-key` | Manage Object Storage access keys |
| `coreweave_object_storage_key_info` | `/v1/cwobject/access-key` | List/get access keys |
| `coreweave_object_storage_policy` | `/v1/cwobject/access-policy` | Manage access policies |
| `coreweave_object_storage_policy_info` | `/v1/cwobject/access-policy` | List access policies |
| `coreweave_object_storage_bucket_info` | `/v1/cwobject/bucket-info` | List/get bucket info |

### Kubernetes CRD Modules

| Module | CRD | Description |
|--------|-----|-------------|
| `coreweave_virtual_server` | `virtualservers.coreweave.com/v1alpha1` | Manage VirtualServer instances |
| `coreweave_virtual_server_info` | `virtualservers.coreweave.com/v1alpha1` | List/get VirtualServers |
| `coreweave_inference_service` | `serving.kubeflow.org/v1beta1` | Manage KServe InferenceService |
| `coreweave_inference_service_info` | `serving.kubeflow.org/v1beta1` | List/get InferenceServices |
| `coreweave_node_pool` | `compute.coreweave.com/v1alpha1` | Manage CKS Node Pools |
| `coreweave_node_pool_info` | `compute.coreweave.com/v1alpha1` | List/get Node Pools |
| `coreweave_pvc` | `v1` | Manage PersistentVolumeClaims |
| `coreweave_pvc_info` | `v1` | List/get PVCs |

### Inventory Plugin

| Plugin | Description |
|--------|-------------|
| `coreweave` | Dynamic inventory from CKS clusters via REST + K8s APIs |

### EDA Event Source Plugins

| Plugin | Description |
|--------|-------------|
| `webhook` | HTTP listener for Grafana/Prometheus/custom alerts |
| `k8s_events` | K8s event watcher for CKS cluster events |

## Requirements

- Ansible >= 2.16.0
- Python >= 3.12
- `kubernetes` Python library >= 28.1.0
- `kubernetes.core` Ansible collection >= 2.4.0

## Installation

```bash
ansible-galaxy collection install stevefulme1.coreweave
```

## Authentication

### REST API modules (CKS, VPC, Object Storage)

REST modules use Bearer token auth against `api.coreweave.com`:

```yaml
- name: Create a CKS cluster
  stevefulme1.coreweave.coreweave_cks_cluster:
    api_token: "{{ lookup('env', 'COREWEAVE_API_TOKEN') }}"
    name: ml-training
    zone: LAS1
    vpc_id: vpc-abc123
    version: v1.32
    pod_cidr_name: pod-cidr
    service_cidr_name: svc-cidr
    state: present
```

### K8s CRD modules (VirtualServer, InferenceService, NodePool, PVC)

CRD modules use standard kubeconfig:

```yaml
- name: Create a GPU VirtualServer
  stevefulme1.coreweave.coreweave_virtual_server:
    kubeconfig: ~/.kube/coreweave-config
    name: my-gpu-vm
    gpu_type: Quadro_RTX_4000
    state: present
```

## Quick Start

```yaml
# Create infrastructure
- stevefulme1.coreweave.coreweave_vpc:
    api_token: "{{ coreweave_token }}"
    name: ml-network
    zone: LAS1
    host_prefix: "10.0.0.0/18"
    prefixes:
      - value: "10.128.0.0/16"
        purpose: pod-cidr

- stevefulme1.coreweave.coreweave_cks_cluster:
    api_token: "{{ coreweave_token }}"
    name: training-cluster
    zone: LAS1
    vpc_id: "{{ vpc_result.vpc.id }}"
    version: v1.32

# Provision GPU nodes
- stevefulme1.coreweave.coreweave_node_pool:
    name: a100-pool
    instance_type: gd-8xa100-i128
    target_nodes: 4
    autoscaling: true

# Deploy inference
- stevefulme1.coreweave.coreweave_inference_service:
    name: llm-endpoint
    container_image: vllm/vllm-openai:latest
    gpu_type: A100_PCIE_80GB
    min_replicas: 1
    max_replicas: 10
```

## EDA Event-Driven Automation

See [docs/eda_rulebooks.md](docs/eda_rulebooks.md) for example rulebooks.

## API Reference

- [CKS API](https://docs.coreweave.com/docs/products/cks/reference/cks-api)
- [VPC API](https://docs.coreweave.com/docs/products/networking/vpc/vpc-api)
- [Object Storage API](https://docs.coreweave.com/docs/products/storage/object-storage/reference/object-storage-api-ref)
- [Node Pool Reference](https://docs.coreweave.com/docs/products/cks/reference/node-pool)

## License

GPL-3.0-or-later

## Author

Steve Fulmer <sfulmer@redhat.com>

## Community

- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
