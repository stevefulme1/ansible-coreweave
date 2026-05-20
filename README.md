# Ansible Collection - stevefulme1.coreweave

Ansible collection for managing CoreWeave cloud infrastructure.

## Status

**All modules, roles, inventory plugins, and EDA event sources have been removed.**

An audit found that every module in this collection used a fabricated REST API
(`https://{host}/api/v1/`) that does not exist. CoreWeave is a Kubernetes-native
cloud platform; automation should use `kubernetes.core.k8s` with CoreWeave CRDs
(VirtualServer, InferenceService, etc.) rather than a proprietary REST API.

The collection skeleton is retained so the repository is not empty, but there
are currently no functional plugins.

## Requirements

- Ansible >= 2.16.0
- Python >= 3.11

## License

Apache-2.0

## Author Information

Steve Fulmer <sfulmer@redhat.com>
