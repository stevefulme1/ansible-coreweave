# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0]

### Added

- 50 modules covering full CoreWeave GPU cloud platform API
- CRUD + info module for every resource type
- EDA source plugins for event-driven automation
- Unit tests and CI pipeline

## [1.0.0-initial] - 2026-05-15

### Added
- Initial release of the CoreWeave Ansible collection
- Core modules for CoreWeave resource management:
  - `coreweave_virtual_server` - Manage VirtualServer CRDs
  - `coreweave_virtual_server_info` - Query VirtualServer resources
  - `coreweave_inference_service` - Manage InferenceService CRDs
  - `coreweave_inference_service_info` - Query InferenceService resources
  - `coreweave_vpc` - Manage VPC resources
  - `coreweave_vpc_info` - Query VPC resources
  - `coreweave_storage_volume` - Manage PersistentVolumeClaims
  - `coreweave_storage_volume_info` - Query storage volumes
  - `coreweave_node_pool_info` - List GPU node pools
- Module utilities:
  - `coreweave_api` - Kubernetes client wrapper for CoreWeave API
- Doc fragments:
  - `coreweave_auth` - Common authentication parameters
- Event-Driven Ansible source plugins:
  - `gpu_availability` - Watch for GPU node availability
  - `events` - Watch Kubernetes events
- Inventory plugin:
  - `coreweave_inventory` - Dynamic inventory from CoreWeave Kubernetes API
- Complete test suite:
  - Unit tests for virtual_server module
  - Integration test placeholders
  - Test fixtures and conftest
- CI/CD workflows:
  - Lint checks with ansible-lint
  - Sanity tests for Ansible 2.16-2.18
  - Unit tests for Python 3.11-3.13
- Documentation:
  - Comprehensive README with examples
  - CONTRIBUTING guidelines
  - CODE_OF_CONDUCT
  - SECURITY policy
  - Example rulebook for EDA

[1.0.0]: https://github.com/stevefulme1/ansible-coreweave/releases/tag/v1.0.0
