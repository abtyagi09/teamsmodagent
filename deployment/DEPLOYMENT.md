# Azure Deployment Guide

## Deploying Teams Moderation System to Azure

This guide covers deploying the Teams moderation system to Azure for production use.

## Prerequisites

- Azure subscription with appropriate permissions
- Azure CLI installed and configured (`az login`)
- Docker (for containerization)
- Azure resources created (see Setup Guide)

## Deployment Options

### Option 1: Azure Container Apps (Recommended)

Azure Container Apps provides a fully managed serverless container platform.

#### Steps

1. **Build and Push Docker Image**

```bash
# Build image
docker build -t teams-moderator:latest .

# Tag for Azure Container Registry
az acr login --name <your-acr-name>
docker tag teams-moderator:latest <your-acr-name>.azurecr.io/teams-moderator:latest

# Push to ACR
docker push <your-acr-name>.azurecr.io/teams-moderator:latest
```

2. **Create Container App Environment**

```bash
az containerapp env create \
  --name teams-mod-env \
  --resource-group <your-rg> \
  --location eastus
```

3. **Deploy Container App**

```bash
az containerapp create \
  --name teams-moderator \
  --resource-group <your-rg> \
  --environment teams-mod-env \
  --image <your-acr-name>.azurecr.io/teams-moderator:latest \
  --registry-server <your-acr-name>.azurecr.io \
  --target-port 8080 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars \
    FOUNDRY_PROJECT_ENDPOINT=secretref:foundry-endpoint \
    FOUNDRY_MODEL_DEPLOYMENT=gpt-4o \
    CONTENT_SAFETY_ENDPOINT=secretref:content-safety-endpoint \
    TEAMS_TENANT_ID=secretref:teams-tenant-id \
    TEAMS_CLIENT_ID=secretref:teams-client-id \
    TEAMS_TEAM_ID=secretref:teams-team-id \
    LOG_LEVEL=INFO
```

4. **Configure Secrets**

```bash
# Add secrets from Key Vault
az containerapp secret set \
  --name teams-moderator \
  --resource-group <your-rg> \
  --secrets \
    foundry-endpoint=<from-keyvault> \
    content-safety-endpoint=<from-keyvault> \
    teams-tenant-id=<from-keyvault> \
    teams-client-id=<from-keyvault> \
    teams-team-id=<from-keyvault> \
    teams-client-secret=<from-keyvault> \
    content-safety-key=<from-keyvault>
```

5. **Enable Managed Identity**

```bash
az containerapp identity assign \
  --name teams-moderator \
  --resource-group <your-rg> \
  --system-assigned
```

### Option 2: Azure Functions

Deploy as a timer-triggered function for periodic scanning.

#### Steps

1. **Create Function App**

```bash
az functionapp create \
  --name teams-moderator-func \
  --resource-group <your-rg> \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --storage-account <your-storage-account>
```

2. **Deploy Function Code**

```bash
func azure functionapp publish teams-moderator-func
```

3. **Configure Timer Trigger**

Edit `function.json`:
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "timer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 */1 * * * *"
    }
  ]
}
```

### Option 3: Azure Kubernetes Service (AKS)

For advanced scenarios with high scalability requirements.

See [kubernetes/README.md](kubernetes/README.md) for detailed K8s deployment.

## Post-Deployment Configuration

### 1. Set Up Monitoring

```bash
# Enable Application Insights
az containerapp logs show \
  --name teams-moderator \
  --resource-group <your-rg> \
  --follow
```

### 2. Configure Auto-Scaling

```bash
az containerapp update \
  --name teams-moderator \
  --resource-group <your-rg> \
  --min-replicas 1 \
  --max-replicas 10 \
  --scale-rule-name cpu-scaling \
  --scale-rule-type cpu \
  --scale-rule-metadata "value=70"
```

### 3. Set Up Alerts

Create alerts for:
- High violation rate
- Agent failures
- API rate limiting
- Resource exhaustion

## Security Best Practices

### Use Managed Identity

Remove API keys from configuration and use Azure Managed Identity:

```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
```

### Key Vault Integration

Store all secrets in Azure Key Vault:

```bash
# Create Key Vault
az keyvault create \
  --name teams-mod-keyvault \
  --resource-group <your-rg> \
  --location eastus

# Add secrets
az keyvault secret set \
  --vault-name teams-mod-keyvault \
  --name teams-client-secret \
  --value "<your-secret>"
```

### Network Security

1. Enable VNet integration
2. Use Private Endpoints for:
   - Microsoft Foundry
   - Content Safety
   - Key Vault
3. Configure NSG rules

## Monitoring & Observability

### Application Insights

```bash
# Enable Application Insights
az monitor app-insights component create \
  --app teams-moderator-insights \
  --location eastus \
  --resource-group <your-rg>

# Link to Container App
az containerapp update \
  --name teams-moderator \
  --resource-group <your-rg> \
  --set-env-vars \
    APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>
```

### Log Analytics

Query logs for violations:

```kusto
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "teams-moderator"
| where Log_s contains "violation"
| project TimeGenerated, Log_s
| order by TimeGenerated desc
```

## Cost Optimization

1. **Use Spot Instances** for non-critical workloads
2. **Configure Auto-Shutdown** during off-hours
3. **Monitor API Usage** to avoid overage charges
4. **Use Reserved Capacity** for predictable workloads

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify Managed Identity permissions
   - Check Key Vault access policies

2. **Teams API Rate Limiting**
   - Implement exponential backoff
   - Increase polling interval

3. **Memory Issues**
   - Increase container memory allocation
   - Optimize agent memory usage

## Rollback Procedure

```bash
# List revisions
az containerapp revision list \
  --name teams-moderator \
  --resource-group <your-rg>

# Rollback to previous revision
az containerapp revision activate \
  --name teams-moderator \
  --resource-group <your-rg> \
  --revision <previous-revision-name>
```

## Support

For deployment issues, contact: it-support@russellcellular.com
