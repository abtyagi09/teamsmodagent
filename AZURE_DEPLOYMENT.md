# Azure Container Apps Deployment Guide

## Prerequisites

Before deploying, ensure you have:

1. **Azure CLI** installed
   ```bash
   # Download and install from: https://learn.microsoft.com/cli/azure/install-azure-cli
   az version
   ```

2. **Logged into Azure**
   ```bash
   az login
   ```

3. **Resource Group** created
   ```bash
   az group create --name <your-resource-group> --location eastus
   ```

4. **Environment Variables Ready**
   - FOUNDRY_PROJECT_ENDPOINT
   - FOUNDRY_MODEL_DEPLOYMENT
   - AZURE_SUBSCRIPTION_ID
   - CONTENT_SAFETY_ENDPOINT
   - CONTENT_SAFETY_KEY
   - TEAMS_TENANT_ID
   - TEAMS_CLIENT_ID
   - TEAMS_CLIENT_SECRET
   - TEAMS_TEAM_ID

## Deployment Options

### Option 1: Automated Deployment (Recommended)

```bash
# Set your environment variables
export FOUNDRY_PROJECT_ENDPOINT="https://..."
export FOUNDRY_MODEL_DEPLOYMENT="gpt-4o-mini"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export CONTENT_SAFETY_ENDPOINT="https://..."
export CONTENT_SAFETY_KEY="your-api-key"
export TEAMS_TENANT_ID="your-tenant-id"
export TEAMS_CLIENT_ID="your-client-id"
export TEAMS_CLIENT_SECRET="your-client-secret"
export TEAMS_TEAM_ID="your-team-id"

# Make the script executable
chmod +x deploy-to-aca.sh

# Run deployment
./deploy-to-aca.sh
```

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Create Azure Container Registry

```bash
az acr create \
  --resource-group <your-resource-group> \
  --name teamsmodregistry \
  --sku Basic
```

#### Step 2: Build and Push Images

```bash
# Build UI image
az acr build \
  --registry teamsmodregistry \
  --image teams-mod-ui:latest \
  --file Dockerfile.ui \
  .

# Build Agent image
az acr build \
  --registry teamsmodregistry \
  --image teams-mod-agent:latest \
  --file Dockerfile.agent \
  .
```

#### Step 3: Create Container Apps Environment

```bash
az containerapp env create \
  --name teams-mod-env \
  --resource-group <your-resource-group> \
  --location eastus
```

#### Step 4: Deploy UI Container App

```bash
az containerapp create \
  --name teams-mod-ui-app \
  --resource-group <your-resource-group> \
  --environment teams-mod-env \
  --image teamsmodregistry.azurecr.io/teams-mod-ui:latest \
  --target-port 8501 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    FOUNDRY_PROJECT_ENDPOINT="$FOUNDRY_PROJECT_ENDPOINT" \
    FOUNDRY_MODEL_DEPLOYMENT="$FOUNDRY_MODEL_DEPLOYMENT" \
    AZURE_SUBSCRIPTION_ID="$AZURE_SUBSCRIPTION_ID" \
    CONTENT_SAFETY_ENDPOINT="$CONTENT_SAFETY_ENDPOINT" \
    TEAMS_TENANT_ID="$TEAMS_TENANT_ID" \
    TEAMS_CLIENT_ID="$TEAMS_CLIENT_ID" \
    TEAMS_TEAM_ID="$TEAMS_TEAM_ID" \
    LOG_LEVEL="INFO" \
  --secrets \
    content-safety-key="$CONTENT_SAFETY_KEY" \
    teams-client-secret="$TEAMS_CLIENT_SECRET" \
  --registry-server teamsmodregistry.azurecr.io \
  --registry-username $(az acr credential show --resource-group <your-resource-group> --name teamsmodregistry --query username -o tsv) \
  --registry-password $(az acr credential show --resource-group <your-resource-group> --name teamsmodregistry --query passwords[0].value -o tsv)
```

#### Step 5: Deploy Monitoring Agent

```bash
az containerapp create \
  --name teams-mod-agent-app \
  --resource-group <your-resource-group> \
  --environment teams-mod-env \
  --image teamsmodregistry.azurecr.io/teams-mod-agent:latest \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    FOUNDRY_PROJECT_ENDPOINT="$FOUNDRY_PROJECT_ENDPOINT" \
    FOUNDRY_MODEL_DEPLOYMENT="$FOUNDRY_MODEL_DEPLOYMENT" \
    AZURE_SUBSCRIPTION_ID="$AZURE_SUBSCRIPTION_ID" \
    CONTENT_SAFETY_ENDPOINT="$CONTENT_SAFETY_ENDPOINT" \
    TEAMS_TENANT_ID="$TEAMS_TENANT_ID" \
    TEAMS_CLIENT_ID="$TEAMS_CLIENT_ID" \
    TEAMS_TEAM_ID="$TEAMS_TEAM_ID" \
    MODERATION_MODE="enforce" \
    LOG_LEVEL="INFO" \
  --secrets \
    content-safety-key="$CONTENT_SAFETY_KEY" \
    teams-client-secret="$TEAMS_CLIENT_SECRET" \
  --registry-server teamsmodregistry.azurecr.io \
  --registry-username $(az acr credential show --resource-group <your-resource-group> --name teamsmodregistry --query username -o tsv) \
  --registry-password $(az acr credential show --resource-group <your-resource-group> --name teamsmodregistry --query passwords[0].value -o tsv)
```

## Accessing Your Deployment

### UI Application

Once deployed, get the URL:

```bash
az containerapp show \
  --name teams-mod-ui-app \
  --resource-group <your-resource-group> \
  --query properties.configuration.ingress.fqdn \
  -o tsv
```

Then open: `https://<fqdn>`

### Monitoring Logs

View UI app logs:
```bash
az containerapp logs show \
  --name teams-mod-ui-app \
  --resource-group <your-resource-group>
```

View Agent logs:
```bash
az containerapp logs show \
  --name teams-mod-agent-app \
  --resource-group <your-resource-group>
```

## Scaling

### Scale UI App

```bash
az containerapp update \
  --name teams-mod-ui-app \
  --resource-group <your-resource-group> \
  --min-replicas 2 \
  --max-replicas 5
```

### Scale Agent

```bash
az containerapp update \
  --name teams-mod-agent-app \
  --resource-group <your-resource-group> \
  --min-replicas 1 \
  --max-replicas 3
```

## Updates

To redeploy with updated code:

```bash
# Rebuild images
az acr build \
  --registry teamsmodregistry \
  --image teams-mod-ui:latest \
  --file Dockerfile.ui \
  .

az acr build \
  --registry teamsmodregistry \
  --image teams-mod-agent:latest \
  --file Dockerfile.agent \
  .

# Container Apps automatically pulls the latest image
```

## Cost Estimation

- **Azure Container Registry (Basic)**: ~$5/month
- **Container Apps**: Pay-per-use
  - UI app (0.5 CPU, 1GB RAM): ~$20-30/month
  - Agent app (0.5 CPU, 1GB RAM): ~$20-30/month
- **Total**: ~$45-70/month (baseline)

## Troubleshooting

### Images not found
```bash
# List images in registry
az acr repository list --name teamsmodregistry
```

### Permission issues
```bash
# Check registry credentials
az acr credential show --resource-group <your-resource-group> --name teamsmodregistry
```

### Container not starting
```bash
# Check container logs
az containerapp logs show \
  --name <app-name> \
  --resource-group <your-resource-group> \
  --follow
```

## Security Best Practices

1. **Use Azure Key Vault** for secrets (instead of passing as env vars)
2. **Enable managed identity** for secure authentication
3. **Use private registry** with authentication
4. **Enable HTTPS only** for all endpoints
5. **Set resource limits** to prevent runaway costs
6. **Use network isolation** with Virtual Networks

## Next Steps

1. Deploy the application
2. Access the UI and configure channels
3. Monitor violations in real-time
4. Set up alerts and notifications
5. Integrate with your security monitoring
