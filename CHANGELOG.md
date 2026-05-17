# Changelog

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
