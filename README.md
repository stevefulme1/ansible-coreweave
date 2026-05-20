# Ansible Collection - stevefulme1.coreweave

Ansible collection for managing CoreWeave cloud infrastructure using
Kubernetes-native Custom Resource Definitions (CRDs).

## Overview

CoreWeave is a Kubernetes-native GPU cloud platform. This collection wraps
CoreWeave CRDs (`VirtualServer`, KServe `InferenceService`) and standard
Kubernetes resources (`PersistentVolumeClaim`) with user-friendly Ansible
modules.

Each module builds a correct Kubernetes manifest from simple parameters and
applies it through the Kubernetes dynamic client.

## Modules

| Module | Description |
|--------|-------------|
| `coreweave_virtual_server` | Manage VirtualServer CRD instances (GPU VMs) |
| `coreweave_virtual_server_info` | List/get VirtualServer resources |
| `coreweave_inference_service` | Manage KServe InferenceService resources |
| `coreweave_inference_service_info` | List/get InferenceService resources |
| `coreweave_pvc` | Manage PersistentVolumeClaims (storage) |
| `coreweave_pvc_info` | List/get PVC resources |

## Requirements

- Ansible >= 2.16.0
- Python >= 3.11
- `kubernetes` Python library >= 28.1.0
- `kubernetes.core` Ansible collection >= 2.4.0
- A valid kubeconfig for a CoreWeave Kubernetes cluster

## Installation

```bash
ansible-galaxy collection install stevefulme1.coreweave
```

## Authentication

All modules use standard Kubernetes authentication via kubeconfig:

```yaml
- name: Create a GPU VirtualServer
  stevefulme1.coreweave.coreweave_virtual_server:
    kubeconfig: ~/.kube/coreweave-config
    context: coreweave-production
    name: my-gpu-vm
    gpu_type: Quadro_RTX_4000
    state: present
```

## Quick Start

```yaml
# Provision storage
- stevefulme1.coreweave.coreweave_pvc:
    name: model-weights
    storage_size: 100Gi
    storage_class_name: shared-hdd-ord1
    access_modes: [ReadWriteMany]

# Deploy inference service
- stevefulme1.coreweave.coreweave_inference_service:
    name: sentiment-analyzer
    container_image: coreweave/fastai-sentiment:4
    gpu_type: Quadro_RTX_5000
    container_env:
      - name: STORAGE_URI
        value: pvc://model-weights/sentiment
    min_replicas: 0
    max_replicas: 10

# Launch GPU workstation
- stevefulme1.coreweave.coreweave_virtual_server:
    name: dev-workstation
    region: ORD1
    gpu_type: Quadro_RTX_4000
    cpu_count: 4
    memory: 16Gi
    root_disk_size: 40Gi
    storage_class_name: block-nvme-ord1
    root_disk_source:
      pvc:
        namespace: vd-images
        name: ubuntu2004-nvidia-510-47-03-1-docker-master-20220421-ord1
```

## CRD Reference

- **VirtualServer**: `virtualservers.coreweave.com/v1alpha1` - GPU-accelerated virtual machines
- **InferenceService**: `serving.kubeflow.org/v1beta1` - KServe model serving with autoscaling
- **PersistentVolumeClaim**: `v1` - Standard Kubernetes storage

## License

Apache-2.0

## Author Information

Steve Fulmer <sfulmer@redhat.com>

## Community

- [Contributing](CONTRIBUTING.md) - How to contribute to this project
- [Code of Conduct](CODE_OF_CONDUCT.md) - Ansible Community Code of Conduct
- [Security Policy](SECURITY.md) - How to report security vulnerabilities
- [License](COPYING) - GPL-3.0

