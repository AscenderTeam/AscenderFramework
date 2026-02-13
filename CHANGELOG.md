# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2026-02-13

### Added
- Feature: Added `provideLifecycle` utility function to handle lifecycle hooks for lazy services. This allows services that are not directly injected to still participate in application startup and shutdown events when provided via `LIFECYCLE_TOKENS`.
- Documentation: Updated DI guide with section on Lazy Service Initialization & Lifecycle.

### Fixed
- Core: Ensure `LIFECYCLE_TOKENS` provider handles nested lists flattened automatically.
