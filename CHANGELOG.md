# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with modular design
- Core model classes (Person, Population, OpenABMCovid19)
- Parameter classes for disease, network, intervention, and vaccine configuration
- Analysis tools for ensemble simulations and scenario comparison
- Visualization utilities for plotting simulation results
- Cloud deployment configurations for AWS, GCP, and Azure
- Docker containerization with multi-service setup
- Comprehensive test suite with unit and integration tests
- GitHub Actions workflows for CI/CD
- Documentation with Sphinx and Jupyter notebooks
- Command-line interface for running simulations
- Utility scripts for environment setup, benchmarking, and deployment

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.0.0] - 2024-01-01

### Added
- Initial release of COVID-19 Agent-Based Model
- Support for 5M+ agent populations
- Enhanced immunity modeling with dual-timescale protection
- Sterilizing and non-sterilizing vaccine scenarios
- Comprehensive intervention modeling (testing, tracing, quarantine)
- Realistic social network generation
- Age-stratified disease progression
- Statistical ensemble analysis
- Cloud-ready deployment architecture
