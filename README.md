# AI-Driven Microsoft Teams Moderation System

An intelligent, multi-agent moderation system for Microsoft Teams built entirely with Azure AI Foundry (formerly Azure AI Foundry). This solution automatically detects, notifies, and removes policy-violating content from Teams channels at scale.

## 🎯 Overview

**Business Challenge**: Russell Cellular's Teams rollout to frontline workforce created moderation challenges that HR cannot handle manually at scale.

**Solution**: Agentic AI system with specialized agents working together to:
- **Moderation Agent**: Analyzes text and images for policy violations using Azure AI Content Safety
- **Notification Agent**: Sends alerts to HR/admins when violations are detected
- **Orchestrator**: Coordinates agents and manages Teams operations (monitoring, deletion)

## 🏗️ Architecture

```
Microsoft Teams Channels
        ↓
   [Webhook/Graph API]
        ↓
    Orchestrator
   /     |     \
Moderation  Notification  Teams Actions
  Agent       Agent      (Delete/Archive)
```

## ✨ Features

- ✅ **Text Moderation**: Detects profanity, harassment, discrimination, PII leaks
- 🖼️ **Image Recognition**: Analyzes images for inappropriate content (future roadmap)
- 🔔 **Real-time Notifications**: Alerts HR when violations occur
- 🗑️ **Automated Deletion**: Removes violating posts automatically
- ⚙️ **Channel Selection**: Configure which channels to moderate
- 📊 **Audit Trail**: Logs all moderation actions
- 🔐 **Secure**: Uses Azure Managed Identity, no hardcoded credentials

## 🚀 Prerequisites

### Azure Resources Required

1. **Microsoft Foundry Project** (formerly Azure AI Foundry)
   - Deploy a model (recommended: `gpt-4.1` or `gpt-4o`)
   - Note your project endpoint and deployment name

2. **Azure AI Content Safety Service**
   - For text and image moderation
   - Note your endpoint and key

3. **Microsoft Teams with Microsoft Entra ID App Registration**
   - App permissions: `ChannelMessage.Read.All`, `ChannelMessage.Delete`
   - Grant admin consent

4. **Azure Key Vault** (recommended for production)
   - Store API keys and secrets

### Local Development Requirements

- Python 3.11+
- Azure CLI (`az login` configured)
- Microsoft Teams admin access

## 📦 Installation

### 1. Clone and Setup

```bash
cd c:\agents\teamschannelmod
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
# Microsoft Foundry (formerly Azure AI Foundry)
FOUNDRY_PROJECT_ENDPOINT=https://<your-project>.api.azureml.ms
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=<your-resource-group>

# Azure AI Content Safety
CONTENT_SAFETY_ENDPOINT=https://<your-content-safety>.cognitiveservices.azure.com
CONTENT_SAFETY_KEY=<your-key>

# Microsoft Teams
TEAMS_TENANT_ID=<your-tenant-id>
TEAMS_CLIENT_ID=<your-app-client-id>
TEAMS_CLIENT_SECRET=<your-client-secret>
TEAMS_TEAM_ID=<team-id-to-monitor>

# Notification Settings
NOTIFICATION_EMAIL=hr@russellcellular.com
NOTIFICATION_WEBHOOK=<optional-teams-webhook-for-alerts>
```

### 3. Configure Moderated Channels

**Option A: Use the Configuration UI (Recommended)**

```powershell
streamlit run ui/app.py
```

The web interface provides easy configuration for:
- Monitored and excluded channels
- Moderation policies and thresholds
- Connection testing
- System settings review

See [UI Documentation](ui/README.md) for details.

**Option B: Edit JSON Files Manually**

Edit `config/channels.json` to specify which channels to monitor:

```json
{
  "monitored_channels": [
    "general",
    "frontline-chat",
    "operations"
  ],
  "excluded_channels": [
    "hr-private",
    "executives"
  ]
}
```

### 4. Configure Moderation Policies

Edit `config/policies.json` to define your content policies:

```json
{
  "text_policies": {
    "hate_speech": {
      "enabled": true,
      "threshold": "medium",
      "action": "delete"
    },
    "profanity": {
      "enabled": true,
      "threshold": "high",
      "action": "flag"
    }
  }
}
```

## 🎬 Usage

### Run the Moderation System

```bash
python src/main.py
```

### Test Mode (Dry Run)

```bash
python src/main.py --dry-run
```

### Monitor Specific Channel

```bash
python src/main.py --channel "frontline-chat"
```

## 📁 Project Structure

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
│   │   └── content_safety.py       # Azure Content Safety
│   ├── utils/
│   │   ├── logging_config.py
│   │   └── config_loader.py
│   └── main.py                     # Entry point
├── config/
│   ├── channels.json               # Channel configuration
│   └── policies.json               # Moderation policies
├── tests/
│   ├── test_moderation.py
│   └── test_workflow.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔧 Deployment to Azure

### Option 1: Azure Container Apps

```bash
az containerapp create \
  --name teams-moderator \
  --resource-group <your-rg> \
  --environment <your-env> \
  --image <your-acr>.azurecr.io/teams-moderator:latest \
  --managed-identity system
```

### Option 2: Azure Functions

Deploy as a timer-triggered function to poll Teams channels periodically.

See [deployment/README.md](deployment/README.md) for detailed instructions.

## 📊 Monitoring & Logging

- All moderation actions logged to `logs/moderation.log`
- Azure Application Insights integration available
- View metrics: violations detected, false positives, response times

## 🛡️ Security Best Practices

1. **Use Managed Identity** in production (no keys in code)
2. **Store secrets in Azure Key Vault**
3. **Enable audit logging** for compliance
4. **Review moderation decisions** weekly to tune policies
5. **Implement role-based access** for admin functions

## 🤝 Contributing

This is a custom solution for Russell Cellular. For support, contact the IT team.

## 📄 License

Proprietary - Russell Cellular Internal Use Only

## 🆘 Support

For issues or questions:
- Email: it-support@russellcellular.com
- Teams: @IT-Support-Team

---

**Built with Microsoft Agent Framework & Azure AI Foundry** 🚀
