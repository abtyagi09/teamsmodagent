# Teams Channel Moderation - Multi-Agent Custom Automation Engine

AI-powered content moderation system for Microsoft Teams using Azure AI Foundry, Content Safety, and multi-agent orchestration following the [Multi-Agent Custom Automation Engine Solution Accelerator](https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator) patterns.

## Solution Overview

This solution provides intelligent, real-time content moderation for Microsoft Teams channels using a multi-agent architecture that combines Azure AI Content Safety with Microsoft Foundry agents for context-aware moderation decisions.

### Key Features

- **🔄 Real-time Monitoring**: Polls Teams channels every 60 seconds for new messages
- **🤖 AI-Powered Detection**: Uses Azure AI Content Safety + Microsoft Foundry agents for intelligent moderation
- **🏗️ Multi-Agent Architecture**: Orchestrates moderation, notification, and decision agents
- **📧 Smart Notifications**: Sends alerts via Azure Communication Services
- **⚙️ Flexible Policies**: Configurable rules for hate speech, harassment, profanity, PII detection
- **📊 Web Dashboard**: Streamlit UI for configuration, monitoring, and analytics
- **🔧 Easy Configuration**: Set up policies and channels through the web interface

## Architecture

The solution follows Microsoft's Multi-Agent Custom Automation Engine patterns:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Microsoft Teams │────▶│  Moderation      │────▶│  Notification   │
│   (Messages)    │     │  Agent           │     │  Agent          │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Azure AI        │
                        │  Content Safety  │
                        │  + AI Foundry    │
                        └──────────────────┘
```

## Quick Start

### Prerequisites

- [Azure Developer CLI (azd) 1.18.0+](https://aka.ms/install-azd)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for local development)
- Azure subscription with appropriate permissions
- Microsoft Teams team to monitor
- **Microsoft Entra ID app registration** - See [Teams Entra ID Setup Guide](docs/TEAMS_ENTRA_SETUP.md)

### Deploy to Azure

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator)

1. **Clone and Initialize**
   ```bash
   git clone <your-repository-url>
   cd teamschannelmod
   ```

2. **Configure Teams Integration**
   
   **📋 Setup Guide:** Follow [Teams Entra ID Setup Guide](docs/TEAMS_ENTRA_SETUP.md) to:
   - Create Entra ID app registration
   - Configure Microsoft Graph permissions
   - Generate client secrets
   - Find Team and Channel IDs
   
   Then update your deployment:
   ```bash
   azd env set TEAMS_TENANT_ID "your-tenant-id"
   azd env set TEAMS_CLIENT_ID "your-client-id"
   azd env set TEAMS_CLIENT_SECRET "your-client-secret"
   azd env set TEAMS_TEAM_ID "your-team-id"
   ```

3. **Deploy Infrastructure**
   ```bash
   azd up
   ```
   
   This will:
   - Create Azure Container Registry
   - Build and push Docker images  
   - Create Container Apps environment
   - Deploy moderation agent and UI
   - Configure managed identity and roles

4. **Configure Through UI**
   
   After deployment, access the UI dashboard at the URL provided by `azd up` and:
   - Configure moderation policies
   - Set up Teams channels to monitor
   - Save configuration to Azure App Configuration
   
   ⚠️ **Important**: The agent requires configuration through the UI before it can function.

## Configuration

All configuration is managed through the web dashboard:

### Moderation Policies
- Hate speech detection thresholds
- Harassment and bullying detection
- Profanity filtering
- Violence and self-harm detection
- PII (Personal Identifiable Information) detection
- Custom response actions (flag, delete, notify)

### Teams Integration
- Select channels to monitor
- Exclude specific channels (e.g., private channels)
- Configure monitoring intervals
- Set notification preferences

## Development

### Local Development Setup

Follow the [Local Development Setup Guide](docs/LocalDevelopmentSetup.md) for detailed instructions.

Quick local setup:
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure resource details

# Run locally
python -m src.main
streamlit run ui/app.py  # In separate terminal
```

### Testing

```bash
# Run all tests
python -m pytest tests/

# Test specific components
python tests/test_moderation.py
python tests/test_email.py
```

## Project Structure

```
teamschannelmod/
├── src/
│   ├── agents/
│   │   ├── moderation_agent.py    # Content moderation logic
│   │   └── notification_agent.py   # Alert handling
│   ├── orchestrator/
│   │   └── workflow.py             # Multi-agent orchestration
│   ├── integrations/
│   │   ├── teams_client.py         # Microsoft Graph API
│   │   └── service_bus_consumer.py # Azure Service Bus
│   ├── utils/
│   │   ├── logging_config.py
│   │   └── config_loader.py
│   └── main.py                     # Entry point
├── ui/
│   └── app.py                      # Streamlit dashboard
├── config/
│   ├── channels.json               # Channel configuration
│   └── policies.json               # Moderation policies
├── infra/
│   └── main.bicep                  # Azure infrastructure
├── docs/
│   ├── DeploymentGuide.md          # Detailed deployment instructions
│   └── LocalDevelopmentSetup.md   # Local setup guide
├── tests/
├── azure.yaml                      # Azure Developer CLI configuration
└── README.md
```

## Deployment Options

### Azure Container Apps (Recommended)
Uses `azd up` for fully automated deployment with:
- Scalable container hosting
- Managed identity integration
- Built-in monitoring and logging

### Manual Azure Deployment
See [docs/DeploymentGuide.md](docs/DeploymentGuide.md) for step-by-step manual deployment instructions.

## Monitoring & Troubleshooting

### View Logs
```bash
# Agent logs
azd logs --service agent --follow

# UI logs
azd logs --service ui --follow
```

### Common Issues

**Agent not detecting violations:**
1. Verify managed identity has "Cognitive Services User" role
2. Check policies are configured in the UI
3. Review agent logs for errors

**Email notifications not working:**
1. Verify Azure Communication Services configuration
2. Check sender email domain is verified
3. Review notification agent logs

For detailed troubleshooting, see [docs/TroubleShootingSteps.md](docs/TroubleShootingSteps.md).

## Security

This solution implements security best practices:
- **Managed Identity**: No stored credentials
- **Secure Configuration**: Settings stored in Azure App Configuration
- **Role-Based Access**: Minimal required permissions
- **Audit Logging**: All moderation actions logged

## Documentation

- [Deployment Guide](docs/DeploymentGuide.md) - Comprehensive deployment instructions
- [Local Development Setup](docs/LocalDevelopmentSetup.md) - Development environment setup
- [Configuration Guide](docs/CONFIGURATION_ARCHITECTURE.md) - Detailed configuration options
- [Email Setup](docs/EMAIL_SETUP.md) - Email notification configuration

## Contributing

This project follows the Microsoft Multi-Agent Custom Automation Engine Solution Accelerator patterns. For contributions:

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation for new features
4. Follow Azure development best practices

## Related Resources

- [Multi-Agent Custom Automation Engine Solution Accelerator](https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with Microsoft Agent Framework & Azure AI Foundry 🚀
