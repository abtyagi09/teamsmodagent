# Teams Moderation Setup Guide

## Prerequisites Checklist

Before running the setup, ensure you have:

### 1. Azure Account
- [ ] Azure subscription active
- [ ] Enough permissions to create resources (Contributor role or higher)

### 2. Azure CLI
- [ ] Installed: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
- [ ] Verified: Run `az --version` in PowerShell

### 3. Authentication
- [ ] Logged into Azure: Run `az login`
- [ ] Correct subscription selected: Run `az account show`

### 4. Configuration Values
Gather these from your `.env` file before starting:
- [ ] `FOUNDRY_PROJECT_ENDPOINT`
- [ ] `FOUNDRY_MODEL_DEPLOYMENT`
- [ ] `AZURE_SUBSCRIPTION_ID`
- [ ] `CONTENT_SAFETY_ENDPOINT`
- [ ] `CONTENT_SAFETY_KEY`
- [ ] `TEAMS_TENANT_ID`
- [ ] `TEAMS_CLIENT_ID`
- [ ] `TEAMS_CLIENT_SECRET`
- [ ] `TEAMS_TEAM_ID`

### 5. Docker (Optional, for testing locally)
- [ ] Docker Desktop installed (if you want to test locally first)
- [ ] Verified: Run `docker --version`

## Quick Start

### Option 1: Automated Setup (Recommended)

```powershell
# Navigate to project directory
cd c:\agents\teamschannelmod

# Run the interactive setup
.\setup-azure.ps1

# Or test it first with dry-run
.\setup-azure.ps1 -DryRun
```

The script will:
1. ✓ Validate Azure CLI
2. ✓ Check Azure login
3. ✓ Create resource group
4. ✓ Build container images
5. ✓ Create Container Apps environment
6. ✓ Deploy UI app
7. ✓ Deploy monitoring agent
8. ✓ Provide access URLs

### Option 2: Manual Setup

If you prefer manual control, follow `AZURE_DEPLOYMENT.md`:

```powershell
# Step 1: Login to Azure
az login

# Step 2: Create resource group
$resourceGroup = "teams-mod-rg"
$region = "eastus"
az group create --name $resourceGroup --location $region

# Step 3: Create container registry
$registryName = "teamsmod$(Get-Random -Minimum 1000 -Maximum 9999)"
az acr create --resource-group $resourceGroup --name $registryName --sku Basic

# Continue following AZURE_DEPLOYMENT.md for remaining steps...
```

## What Gets Deployed

### UI Application
- **Name**: `teams-mod-ui-app`
- **Type**: Streamlit web interface
- **Port**: 8501
- **Resources**: 0.5 CPU, 1GB RAM
- **Scaling**: 1-5 replicas (auto-scales based on demand)
- **Access**: HTTPS URL provided after deployment

### Monitoring Agent
- **Name**: `teams-mod-agent-app`
- **Type**: Python background service
- **Function**: Continuously monitors Teams channels
- **Resources**: 0.5 CPU, 1GB RAM
- **Runs**: 24/7 in background
- **Detection**: Enforces moderation policies in real-time

### Infrastructure
- **Container Registry**: Stores your Docker images
- **Container Apps Environment**: Manages both applications
- **Managed**: Automatically handles scaling, updates, health checks

## Access Your Deployment

### UI Dashboard
Once deployed, access your configuration dashboard:
```
https://<your-fqdn>.azurecontainerapps.io
```

The script will display this URL when complete.

### Check Logs

```powershell
# View UI logs
az containerapp logs show --name teams-mod-ui-app --resource-group teams-mod-rg

# View Agent logs
az containerapp logs show --name teams-mod-agent-app --resource-group teams-mod-rg

# Live stream logs
az containerapp logs show --name teams-mod-ui-app --resource-group teams-mod-rg --follow
```

## Common Issues

### "Not logged into Azure"
```powershell
az login
```

### "Azure CLI not found"
Install from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

### "Insufficient permissions"
Contact your Azure admin to grant `Contributor` role on your subscription.

### "Container build failed"
- Ensure you're in the project directory: `cd c:\agents\teamschannelmod`
- Check Docker is running if testing locally
- Run manually: `az acr build --registry <name> --image teams-mod-ui:latest --file Dockerfile.ui .`

### "Deployment timeout"
Azure resources can take 2-5 minutes to initialize. Wait and try:
```powershell
az containerapp show --name teams-mod-ui-app --resource-group teams-mod-rg
```

## Estimated Costs

| Resource | Monthly Cost |
|----------|--------------|
| Container Apps (2 apps) | $40-60 |
| Container Registry | $5 |
| Data egress (if any) | $0-10 |
| **Total** | **~$45-75** |

Costs vary by region and usage. Use Azure pricing calculator for exact estimates.

## Next Steps After Deployment

1. **Access UI Dashboard**
   - Open the provided HTTPS URL
   - Log in (if required)
   - Configure channels to monitor

2. **Monitor Violations**
   - Check Real-time logs
   - Review violation alerts
   - Adjust policies as needed

3. **Set Up Notifications** (Optional)
   - Add email alerts
   - Integrate with Teams for notifications
   - Create escalation workflows

4. **Add to CI/CD** (Optional)
   - Automate deployments
   - Version control images
   - Set up staging environment

## Support

### Documentation
- 📖 **Architecture**: See `ARCHITECTURE.md`
- 🚀 **Deployment**: See `AZURE_DEPLOYMENT.md`
- 🔍 **API Limits**: See `DELETION_PERMISSIONS.md`
- ⚡ **Quick Start**: See `QUICKSTART.md`

### Repository
- 📦 GitHub: https://github.com/abtyagi09/teamsmodagent
- 📋 Issues: Report via GitHub issues

### Command Help
```powershell
# Get help for any az command
az containerapp --help
az acr --help
az group --help
```

## Rollback/Cleanup

If you need to remove everything:

```powershell
# Delete resource group (removes everything)
az group delete --name teams-mod-rg --yes --no-wait

# Or delete individual resources
az containerapp delete --name teams-mod-ui-app --resource-group teams-mod-rg
az containerapp delete --name teams-mod-agent-app --resource-group teams-mod-rg
az acr delete --name teamsmod<xxxx> --resource-group teams-mod-rg
```

---

**Questions?** Check the documentation files or the GitHub repository.
