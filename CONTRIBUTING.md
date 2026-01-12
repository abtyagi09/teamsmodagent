# Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

## Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## How to Contribute

### Reporting Issues

- Use the issue tracker to report bugs or request features
- Provide clear steps to reproduce any issues
- Include relevant logs and configuration details
- Search existing issues before creating new ones

### Development Setup

1. Follow the [Local Development Setup Guide](docs/LocalDevelopmentSetup.md)
2. Ensure all tests pass before submitting changes
3. Follow the existing code style and patterns
4. Add tests for new functionality

### Pull Request Process

1. Fork the repository and create a feature branch
2. Make your changes following the project conventions
3. Add or update tests as needed
4. Update documentation for any new features
5. Ensure all tests pass
6. Submit a pull request with a clear description

### Code Style Guidelines

**Python Code:**
- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings for classes and functions
- Keep functions focused and modular

**Infrastructure Code:**
- Follow Bicep best practices
- Use descriptive parameter and variable names
- Add comments for complex logic
- Follow Azure naming conventions

**Documentation:**
- Use clear, concise language
- Include code examples where helpful
- Update README.md for significant changes
- Follow Markdown best practices

### Testing Requirements

- All new code must include appropriate tests
- Tests should cover both success and failure scenarios
- Integration tests should verify Azure service interactions
- UI changes should include functional tests

### Architecture Considerations

This project follows the Microsoft Multi-Agent Custom Automation Engine Solution Accelerator patterns:

- **Multi-Agent Architecture**: Separate agents for different responsibilities
- **Azure Integration**: Leverage managed services over custom implementations
- **Security Best Practices**: Use managed identities and secure configuration
- **Scalability**: Design for horizontal scaling and high availability

### Contribution Areas

We welcome contributions in these areas:

**Core Features:**
- Enhanced content moderation algorithms
- Additional notification channels (Teams, Slack, etc.)
- Advanced policy configuration options
- Performance optimizations

**Infrastructure:**
- Bicep template improvements
- Security enhancements
- Monitoring and alerting
- Cost optimization

**Documentation:**
- Setup guides for different environments
- Troubleshooting documentation
- Architecture diagrams
- Best practices guides

**Testing:**
- Unit tests for core functionality
- Integration tests for Azure services
- Performance testing
- Security testing

### Getting Help

- Review the [Documentation](docs/) for guidance
- Check [Troubleshooting Guide](docs/TroubleShootingSteps.md) for common issues
- Open an issue for questions or problems
- Reference the [Microsoft Multi-Agent Custom Automation Engine Solution Accelerator](https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator) for patterns

Thank you for contributing to the Teams Channel Moderation solution!