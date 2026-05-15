# Contributing to CoreWeave Ansible Collection

Thank you for your interest in contributing to the CoreWeave Ansible Collection!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/ansible-coreweave.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests locally
6. Commit and push
7. Open a Pull Request

## Development Setup

Install development dependencies:

```bash
pip install -r requirements.txt
pip install -r tests/requirements.txt
ansible-galaxy collection install kubernetes.core
```

## Code Standards

### Python Code
- Follow PEP 8 style guide
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use descriptive variable and function names

### Ansible Modules
- Follow [Ansible module conventions](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
- Include comprehensive documentation with DOCUMENTATION, EXAMPLES, and RETURN blocks
- Support check mode where applicable
- Return changed status accurately
- Handle errors gracefully with meaningful messages

### Documentation
- Update README.md for new features
- Add examples for new modules
- Update CHANGELOG.md following Keep a Changelog format
- Include docstrings for all Python functions

## Testing

### Run Linting

```bash
ansible-lint
```

### Run Sanity Tests

```bash
ansible-test sanity --docker -v
```

### Run Unit Tests

```bash
pytest tests/unit/ -v
```

### Run Integration Tests

```bash
# Requires access to a CoreWeave cluster
ansible-test integration --docker -v
```

## Adding New Modules

1. Create module file in `plugins/modules/`
2. Add unit tests in `tests/unit/plugins/modules/`
3. Add integration tests in `tests/integration/targets/`
4. Update `meta/runtime.yml` with new module routing
5. Add examples to README.md
6. Update CHANGELOG.md

## Adding New Plugins

### Inventory Plugins
Place in `plugins/inventory/` and add example configuration to README.md

### Event Source Plugins
Place in `extensions/eda/plugins/event_source/` with example rulebooks

## Pull Request Process

1. **Before Submitting**
   - Run all tests locally
   - Update documentation
   - Add changelog entry
   - Ensure code follows style guidelines

2. **PR Description**
   - Clear title describing the change
   - Description of what changed and why
   - Link to any related issues
   - Breaking changes clearly noted

3. **Review Process**
   - At least one maintainer approval required
   - All CI checks must pass
   - Address all review comments

4. **Merging**
   - Maintainers will merge approved PRs
   - Squash merge for feature branches
   - Linear history maintained on main

## Commit Messages

Follow conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(modules): add coreweave_virtual_server module

Add new module for managing CoreWeave VirtualServer CRDs with support
for GPU selection, memory/CPU configuration, and storage volumes.

Closes #123
```

## Code Review Guidelines

When reviewing PRs:
- Be constructive and respectful
- Focus on code quality and maintainability
- Test functionality when possible
- Suggest improvements, don't demand perfection

## Community

- Be respectful and inclusive
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)
- Help others learn and grow
- Share knowledge and best practices

## Questions?

- Open an issue for bugs or feature requests
- Tag issues with appropriate labels
- Provide clear reproduction steps for bugs

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.
