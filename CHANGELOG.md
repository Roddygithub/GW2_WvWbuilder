# Changelog

All notable changes to the GW2 WvW Builder project will be documented in this file.

## [Unreleased]

### Added
- Comprehensive test runner script (`run_tests.sh`) with support for different test types and coverage reporting
- Detailed testing documentation in `TESTING.md`
- GitHub Actions workflow for running tests and reporting coverage
- Test dependencies organized in `pyproject.toml` under `[project.optional-dependencies]`

### Changed
- Updated `pyproject.toml` to use standard Python packaging with `[project.optional-dependencies]`
- Improved test coverage reporting and CI integration
- Streamlined test execution with better error handling and reporting

### Fixed
- Resolved dependency installation issues in CI
- Fixed test environment setup for consistent test execution
- Addressed linting and code style issues in test files

## [0.1.0] - YYYY-MM-DD

### Added
- Initial project setup
- Core functionality implementation
- Basic test suite
