# Changelog

## [0.2.0] - 2026-06-17

### Added
- **REST API modules** (CoreWeave api.coreweave.com):
  - `coreweave_cks_cluster` / `_info` — CKS cluster CRUD (`/v1beta1/cks/clusters`)
  - `coreweave_vpc` / `_info` — VPC CRUD (`/v1beta1/networking/vpcs`)
  - `coreweave_object_storage_key` / `_info` — Object Storage access keys (`/v1/cwobject/access-key`)
  - `coreweave_object_storage_policy` / `_info` — Object Storage policies (`/v1/cwobject/access-policy`)
  - `coreweave_object_storage_bucket_info` — Object Storage bucket info (`/v1/cwobject/bucket-info`)
- **K8s CRD modules**:
  - `coreweave_node_pool` / `_info` — CKS Node Pools (`compute.coreweave.com/v1alpha1`)
- **Inventory plugin**:
  - `coreweave` — dynamic inventory from CKS clusters, groups by GPU type, region, node pool
- **EDA event source plugins** (standalone, no `ansible.eda` dependency):
  - `webhook` — HTTP listener for Grafana/Prometheus/custom alerts
  - `k8s_events` — K8s event watcher for CKS cluster events
- REST API client (`coreweave_api.py`) using `ansible.module_utils.urls`
- REST auth doc fragment for Bearer token authentication
- Example rulebooks in `docs/eda_rulebooks.md`

### Changed
- CI updated: Python 3.12/3.13, ansible-core 2.16/2.18/2.20/2.21
- Added sanity test job (all 4 ansible-core versions pass)
- Replaced flake8 with ruff
- Updated and fixed all unit tests (52 total, all passing)

## [3.0.0] - 2026-05-20

### Added
- `coreweave_virtual_server` module - manage VirtualServer CRD (GPU instances)
- `coreweave_virtual_server_info` module - list/get VirtualServer resources
- `coreweave_inference_service` module - manage KServe InferenceService (model serving)
- `coreweave_inference_service_info` module - list/get InferenceService resources
- `coreweave_pvc` module - manage PersistentVolumeClaims (storage)
- `coreweave_pvc_info` module - list/get PVC resources
- `k8s_helper` module_utils - Kubernetes dynamic client wrapper for CRUD operations
- `auth` doc_fragment - shared authentication documentation

### Changed
- All modules now use Kubernetes-native CRD approach instead of fabricated REST API
- Collection rebuilt from scratch with correct CoreWeave API schemas
- VirtualServer uses `virtualservers.coreweave.com/v1alpha1` CRD
- InferenceService uses `serving.kubeflow.org/v1beta1` (KServe) CRD
- Dependency on `kubernetes.core` collection for K8s API access

### Removed
- All previous fabricated REST API modules (50+ modules)
- Fabricated roles, inventory plugin, and EDA source plugins
- `coreweave_api` module_utils (fake REST client)

## [2.1.2] - 2026-05-18

### Security
- Add `no_log: true` to password and api_key fields in role argument_specs
- Change EDA webhook host default from `0.0.0.0` to `127.0.0.1`
- Add `secret: true` to credential options in inventory plugins


## [2.1.1] - 2026-05-18

### Security
- Prevent credential leak in API request bodies — connection params (host, username, password, api_key, validate_certs) are now stripped before create/update payloads are sent to the remote API
- Add timeout=30 to all HTTP methods to prevent indefinite hangs
- Harden .gitignore to exclude secrets, credentials, and IDE artifacts

## [2.0.0] - 2026-05-17

### Added
- Idempotency: get-before-write with state comparison in 27 modules
- Pagination support (limit/offset) for all _info modules
- 3 operational roles for CoreWeave GPU cloud
- Spot instance, node affinity, billing, and quota modules
- Comprehensive unit and integration test suites
- Pre-commit and linting configuration

### Fixed
- Role README files added for Galaxy compliance
- Galaxy import validation issues resolved
- CI failures resolved

### Security
- Pinned urllib3>=2.6.0 to fix CVE-2025-66471
- Bumped requests>=2.32.5 to fix CVE-2023-32681, CVE-2024-35195

## [1.2.0] - 2026-05-15

### Added
- 50 modules covering full CoreWeave GPU cloud platform API
- 10 Day-2 operation roles
- Dynamic inventory plugin
- EDA source plugins for event-driven automation

## [1.0.1] - 2026-05-15

### Fixed
- Module documentation rendering on Galaxy

## [1.0.0] - 2026-05-15

### Added
- Initial release with core modules for CoreWeave resource management
- EDA source plugins (gpu_availability, events)
- Inventory plugin
- Unit tests and CI pipeline
