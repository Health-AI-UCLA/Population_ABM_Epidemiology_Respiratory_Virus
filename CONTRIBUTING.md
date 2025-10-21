# Contributing to COVID-19 ABM

Thank you for your interest in contributing to the COVID-19 Agent-Based Model! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows a code of conduct that we expect all contributors to adhere to. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/Health-AI-UCLA/Population_ABM_Epidemiology_Respiratory_Virus.git
   cd Population_ABM_Epidemiology_Respiratory_Virus
   ```

2. **Set up the development environment**
   ```bash
   ./scripts/setup_environment.sh
   ```

3. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

4. **Run tests to verify setup**
   ```bash
   pytest tests/
   ```

## Development Workflow

### Branching Strategy

We use a Git Flow branching model:

- `main`: Production-ready releases
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `hotfix/*`: Critical bug fixes
- `release/*`: Release preparation branches

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and linting**
   ```bash
   pytest tests/
   flake8 src tests
   mypy src/covid_abm
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(component): description of changes"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style Guidelines

### Python Style

We follow PEP 8 with some modifications:

- Maximum line length: 127 characters
- Use type hints for all function signatures
- Use docstrings for all public functions and classes
- Use meaningful variable and function names

### Code Formatting

We use Black for code formatting and flake8 for linting:

```bash
black src tests
flake8 src tests
```

### Type Checking

We use mypy for static type checking:

```bash
mypy src/covid_abm
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=covid_abm --cov-report=html

# Run specific test file
pytest tests/test_model.py

# Run with verbose output
pytest tests/ -v
```

### Writing Tests

- Write unit tests for individual functions and methods
- Write integration tests for complete workflows
- Aim for high test coverage (>90%)
- Use descriptive test names
- Include both positive and negative test cases

### Test Structure

```python
def test_function_name():
    """Test description."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

## Documentation

### Code Documentation

- All public functions and classes must have docstrings
- Use Google-style docstrings
- Include type hints in function signatures
- Provide examples in docstrings for complex functions

### API Documentation

API documentation is automatically generated from docstrings using Sphinx.

### Tutorial Documentation

Tutorials are written as Jupyter notebooks in `docs/notebooks/`.

## Pull Request Process

### Before Submitting

1. Ensure all tests pass
2. Run linting and type checking
3. Update documentation if needed
4. Add tests for new functionality
5. Update CHANGELOG.md if applicable

### Pull Request Template

When creating a pull request, please fill out the template completely:

- Description of changes
- Type of change (bug fix, feature, etc.)
- Related issues
- Testing performed
- Documentation updates

### Review Process

- All PRs require at least 2 reviewer approvals
- Automated tests must pass
- Code coverage must not decrease
- Documentation must be updated

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment information (OS, Python version, etc.)
- Error messages and stack traces

### Feature Requests

When requesting features, please include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (if you have ideas)
- Research relevance

## Research Contributions

We welcome contributions from the research community:

### Model Validation

- Help validate model parameters against real-world data
- Contribute epidemiological insights
- Suggest improvements to disease progression models

### New Features

- Implement new intervention strategies
- Add support for new vaccine types
- Enhance network generation algorithms

### Performance Optimization

- Optimize simulation performance
- Improve memory usage
- Add parallel processing capabilities

## Release Process

### Version Numbering

We follow Semantic Versioning (MAJOR.MINOR.PATCH):

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist

1. Update version numbers in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release tag
6. Publish to PyPI

## Getting Help

- Check existing issues and discussions
- Join our community discussions
- Contact maintainers for urgent issues

## Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to COVID-19 ABM!
