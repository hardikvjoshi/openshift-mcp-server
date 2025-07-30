# Contributing to OpenShift MCP Server

Thank you for your interest in contributing to the OpenShift MCP Server project! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

- Use the GitHub issue tracker
- Include detailed steps to reproduce the bug
- Provide environment information (OS, Python version, OpenShift version)
- Include error messages and logs

### Suggesting Enhancements

- Use the GitHub issue tracker with the "enhancement" label
- Describe the feature and its benefits
- Provide use cases and examples

### Pull Requests

- Fork the repository
- Create a feature branch
- Make your changes
- Add tests if applicable
- Update documentation
- Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8+
- OpenShift cluster access
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/openshift-mcp-server.git
   cd openshift-mcp-server
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your cluster credentials
   ```

5. **Run tests**
   ```bash
   python test_openshift_mcp.py
   ```

## Pull Request Process

1. **Fork and clone** the repository
2. **Create a feature branch** from `main`
3. **Make your changes** following the code style guidelines
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Run tests** to ensure everything works
7. **Commit your changes** with clear commit messages
8. **Push to your fork** and create a pull request

### Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(server): add new cluster health monitoring tool`
- `fix(cluster): resolve connection timeout issue`
- `docs(readme): update installation instructions`

## Code Style

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep functions focused and small
- Add docstrings for all public functions
- Use meaningful variable and function names

### Example

```python
def list_namespaces(self) -> List[Dict[str, Any]]:
    """
    List all namespaces/projects in the cluster.
    
    Returns:
        List[Dict[str, Any]]: List of namespace information dictionaries
        
    Raises:
        Exception: If connection fails or API error occurs
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Error listing namespaces: {e}")
        return []
```

## Testing

### Running Tests

```bash
# Run all tests
python test_openshift_mcp.py

# Run with verbose output
python -v test_openshift_mcp.py
```

### Writing Tests

- Test both success and failure scenarios
- Mock external dependencies when appropriate
- Use descriptive test names
- Include edge cases

### Example Test

```python
def test_list_namespaces_success(self):
    """Test successful namespace listing."""
    cluster = OpenShiftCluster(self.cluster_url, self.token)
    namespaces = cluster.list_namespaces()
    
    self.assertIsInstance(namespaces, list)
    self.assertGreater(len(namespaces), 0)
    
    for ns in namespaces:
        self.assertIn('name', ns)
        self.assertIn('status', ns)
```

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Include parameter descriptions and return types
- Provide usage examples for complex functions

### Project Documentation

- Update README.md for new features
- Add examples to QUICKSTART.md
- Update PROJECT_DOCUMENTATION.md for significant changes

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI changes
- Keep documentation up to date

## Getting Help

If you need help with contributing:

1. Check existing issues and pull requests
2. Read the documentation
3. Ask questions in GitHub discussions
4. Contact maintainers directly

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to OpenShift MCP Server! 🚀 