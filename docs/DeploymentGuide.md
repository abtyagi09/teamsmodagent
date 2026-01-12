# Deployment Guide

## Overview

This guide walks you through deploying the Teams Channel Moderation solution to Azure. The deployment process takes approximately 5-7 minutes and includes both infrastructure provisioning and application setup.

🆘 **Need Help?** If you encounter any issues during deployment, check our [Troubleshooting Guide](TroubleShootingSteps.md) for solutions to common problems.

---

## Step 1: Prerequisites & Setup

### 1.1 Azure Account Requirements

Ensure you have access to an [Azure subscription](https://azure.microsoft.com/free/) with the following permissions:

| **Required Permission/Role** | **Scope** | **Purpose** |
|------------------------------|-----------|-------------|
| **Contributor** | Subscription level | Create and manage Azure resources |
| **User Access Administrator** | Subscription level | Manage user access and role assignments |
| **Role Based Access Control** | Subscription/Resource Group level | Configure RBAC permissions |
| **App Registration Creation** | Azure Active Directory | Create and configure authentication |

### 1.2 Check Service Availability & Quota

⚠️ **CRITICAL:** Before proceeding, ensure your chosen region has all required services available:

**Required Azure Services:**
- [Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Container Registry](https://learn.microsoft.com/en-us/azure/container-registry/)
- [Azure Communication Services](https://learn.microsoft.com/en-us/azure/communication-services/)
- [Azure App Configuration](https://learn.microsoft.com/en-us/azure/azure-app-configuration/)
- [Azure Service Bus](https://learn.microsoft.com/en-us/azure/service-bus/)

**Recommended Regions:** East US, East US2, West US2, North Central US

---

## Step 2: Choose Your Deployment Environment

### Option A: GitHub Codespaces (Easiest)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator)

1. Click the badge above (may take several minutes to load)
2. Accept default values on the Codespaces creation page
3. Wait for the environment to initialize (includes all deployment tools)
4. Proceed to [Step 3: Deploy the Solution](#step-3-deploy-the-solution)

### Option B: Local Environment

**Required Tools:**
- [PowerShell 7.0+](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell) 
- [Azure Developer CLI (azd) 1.18.0+](https://aka.ms/install-azd)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/downloads)

**Setup Steps:**
1. Install all required deployment tools listed above
2. Clone the repository:
   ```shell
   git clone <your-repository-url>
   cd teamschannelmod
   ```
3. Proceed to [Step 3: Deploy the Solution](#step-3-deploy-the-solution)

---

## Step 3: Deploy the Solution

### 3.1 Authenticate with Azure

```shell
azd auth login
```

### 3.2 Start Deployment

```shell
azd up
```

**During deployment, you'll be prompted for:**
1. **Environment name** (e.g., "teamsmod") - Must be 3-16 characters long, alphanumeric only
2. **Azure subscription** selection
3. **Azure AI Foundry deployment region** - Select a region with available model quota
4. **Primary location** - Select the region where your infrastructure resources will be deployed
5. **Resource group** selection (create new or use existing)

**Expected Duration:** 5-7 minutes for default configuration

Upon successful completion, you will see a success message indicating that all resources have been deployed, along with the application URL and next steps.

---

## Step 4: Post-Deployment Configuration

### 4.1 Configure Teams Integration

**⚠️ IMPORTANT:** Before configuring the UI, you must set up Entra ID app registration for Teams access.

**📋 Complete Setup Guide:** See [Teams Entra ID Setup Guide](TEAMS_ENTRA_SETUP.md) for detailed instructions on:
- Creating Entra ID app registration
- Configuring Microsoft Graph API permissions  
- Generating client secrets
- Finding Team IDs and channel information
- Security best practices

**Quick Configuration Steps:**
1. **Complete Entra ID Setup** following the [detailed guide](TEAMS_ENTRA_SETUP.md)
2. **Update Environment Variables:**
   ```bash
   azd env set TEAMS_TENANT_ID "your-tenant-id"
   azd env set TEAMS_CLIENT_ID "your-client-id"
   azd env set TEAMS_CLIENT_SECRET "your-client-secret"  
   azd env set TEAMS_TEAM_ID "your-team-id"
   azd up  # Redeploy with new configuration
   ```
3. **Access the UI Dashboard** at the URL provided by `azd up`
4. **Configure Teams Channel Selection:**
   - Select specific channels to monitor
   - Exclude sensitive channels (HR, executive, etc.)
   - Set monitoring frequency (default: 60 seconds)

### 4.2 Configure Moderation Policies

Set up content moderation rules:
- **Hate Speech Detection**: Configure sensitivity levels
- **Harassment Detection**: Set bullying and intimidation thresholds  
- **Profanity Filter**: Define inappropriate language handling
- **Violence/Self-harm**: Set detection parameters
- **PII Detection**: Configure personal information detection

### 4.3 Configure Email Notifications

Set up Azure Communication Services for email alerts:
- **Email Connection String**: From Azure Communication Services
- **Sender Email**: Must be from verified ACS domain
- **Notification Recipients**: Email addresses to receive alerts

### 4.4 Save Configuration

**⚠️ CRITICAL:** Click "Save Configuration" in the UI to store all settings in Azure App Configuration. The agent will not function until configuration is saved.

---

## Step 5: Verify Deployment

### 5.1 Check Agent Status

```shell
# View agent logs
azd logs --service agent --follow

# Check if agent is processing messages
azd logs --service agent --tail 50 | grep "Processing message"
```

### 5.2 Test Email Notifications

From the UI dashboard:
1. Navigate to the "Test" section
2. Click "Send Test Email"
3. Verify email is received at configured address

### 5.3 Monitor Teams Channels

The agent will begin monitoring configured Teams channels within 60 seconds of saving configuration.

---

## Step 6: Clean Up (Optional)

To remove all deployed resources:

```shell
azd down
```

**⚠️ Warning:** This will permanently delete all resources and data.

---

## Managing Multiple Environments

### Creating a New Environment

```shell
# Create a new environment
azd env new teamsmod-prod

# Switch to the new environment
azd env select teamsmod-prod

# Deploy to the new environment
azd up
```

### Switch Between Environments

```shell
# List available environments
azd env list

# Switch to different environment
azd env select <environment-name>
```

---

## Troubleshooting

### Common Deployment Issues

**Azure OpenAI Quota Exceeded:**
- Try a different region with available quota
- Request additional quota in Azure Portal

**Container App Startup Failures:**
- Check logs: `azd logs --service agent --tail 100`
- Verify all required environment variables are set
- Ensure managed identity has proper role assignments

**Configuration Not Saving:**
- Verify Azure App Configuration service is deployed
- Check managed identity has "App Configuration Data Owner" role
- Review UI logs: `azd logs --service ui --tail 50`

For detailed troubleshooting steps, see [TroubleShootingSteps.md](TroubleShootingSteps.md).

---

## Next Steps

Once deployment is complete:

1. **Configure the System**: Use the web dashboard to set up policies and channels
2. **Monitor Operations**: Review logs and adjust policies based on detected content
3. **Scale as Needed**: Adjust Container Apps scaling rules based on Teams usage

📚 **Additional Resources:**
- [Configuration Guide](CONFIGURATION_ARCHITECTURE.md) - Detailed configuration options
- [Local Development Setup](LocalDevelopmentSetup.md) - Set up development environment
- [Email Setup Guide](EMAIL_SETUP.md) - Configure email notifications

---

## Need Help?

- 🐛 **Issues:** Check [TroubleShootingSteps.md](TroubleShootingSteps.md)
- 📖 **Documentation:** Review configuration guides
- 💬 **Support:** Contact your system administrator