# Ansible Collection - stevefulme1.coreweave

Ansible collection for managing CoreWeave cloud infrastructure.

## Description

This collection provides Ansible modules and plugins for managing CoreWeave cloud resources, including GPU virtual servers, inference services, VPCs, storage volumes, and more. CoreWeave is a Kubernetes-native cloud platform, and this collection leverages Kubernetes CRDs for resource management.

## Requirements

- Ansible >= 2.16.0
- Python >= 3.11
- kubernetes.core collection >= 2.4.0
- Python packages:
  - kubernetes >= 29.0.0
  - PyYAML >= 6.0

## Installation

Install from Ansible Galaxy:

```bash
ansible-galaxy collection install stevefulme1.coreweave
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Authentication

CoreWeave uses Kubernetes authentication. You can authenticate using:

1. Kubeconfig file (default: `~/.kube/config`)
2. API token
3. In-cluster service account (for pods running in CoreWeave)

Example kubeconfig setup:

```yaml
- name: Manage CoreWeave resources
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create a virtual server
      stevefulme1.coreweave.coreweave_virtual_server:
        name: my-gpu-vm
        namespace: tenant-example
        gpu_type: RTX_A5000
        gpu_count: 1
        memory: 16Gi
        cpu_count: 4
        state: present
```

## Modules

### Virtual Server Management
- `coreweave_virtual_server` - Manage CoreWeave VirtualServer resources
- `coreweave_virtual_server_info` - Get information about VirtualServers

### Inference Services
- `coreweave_inference_service` - Manage CoreWeave InferenceService resources
- `coreweave_inference_service_info` - Get information about InferenceServices

### Networking
- `coreweave_vpc` - Manage CoreWeave VPC resources
- `coreweave_vpc_info` - Get information about VPCs

### Storage
- `coreweave_storage_volume` - Manage CoreWeave PersistentVolumeClaims
- `coreweave_storage_volume_info` - Get information about storage volumes

### Informational
- `coreweave_node_pool_info` - List available GPU node pools

## Inventory Plugin

The `coreweave_inventory` plugin provides dynamic inventory from the CoreWeave Kubernetes API:

```yaml
# inventory.coreweave.yml
plugin: stevefulme1.coreweave.coreweave_inventory
namespaces:
  - tenant-example
  - tenant-prod
connections:
  - name: default
    kubeconfig: ~/.kube/config
```

## Event-Driven Ansible Plugins

### Source Plugins

#### gpu_availability
Watch for GPU node availability changes:

```yaml
- name: GPU Availability Watcher
  hosts: all
  sources:
    - stevefulme1.coreweave.gpu_availability:
        kubeconfig: ~/.kube/config
        gpu_types:
          - RTX_A6000
          - A100_NVLINK
  rules:
    - name: Alert on GPU availability
      condition: event.gpu_available == true
      action:
        debug:
          msg: "{{ event.gpu_type }} is now available"
```

#### events
Watch Kubernetes events in CoreWeave:

```yaml
- name: CoreWeave Event Watcher
  hosts: all
  sources:
    - stevefulme1.coreweave.events:
        kubeconfig: ~/.kube/config
        namespace: tenant-example
        event_types:
          - Warning
          - Error
  rules:
    - name: Alert on warnings
      condition: event.type == "Warning"
      action:
        debug:
          msg: "Warning: {{ event.message }}"
```

## Example Playbooks

### Create a GPU Virtual Server

```yaml
- name: Deploy GPU workload
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create virtual server
      stevefulme1.coreweave.coreweave_virtual_server:
        name: ml-training-vm
        namespace: tenant-ml
        gpu_type: A100_NVLINK_80GB
        gpu_count: 8
        memory: 256Gi
        cpu_count: 32
        storage:
          - name: data
            size: 1Ti
            storage_class: block-nvme-ord1
        state: present
      register: vm_result

    - name: Display VM info
      debug:
        msg: "VM created: {{ vm_result.resource.status.phase }}"
```

### Deploy an Inference Service

```yaml
- name: Deploy inference endpoint
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create inference service
      stevefulme1.coreweave.coreweave_inference_service:
        name: llama-inference
        namespace: tenant-ai
        model_name: llama2-70b
        gpu_type: A100_NVLINK_80GB
        gpu_count: 4
        replicas: 2
        state: present
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Security

See [SECURITY.md](SECURITY.md) for security policy and reporting vulnerabilities.

## License

Apache-2.0

## Author Information

Steve Fulmer <sfulmer@redhat.com>

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/stevefulme1/ansible-coreweave/issues).
