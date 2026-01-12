# Azure Resource Setup Guide

## Setting Up Azure Resources for Teams Moderation

This guide walks you through creating all required Azure resources.

## 1. Microsoft Foundry Project Setup

### Create a Microsoft Foundry Project

1. **Navigate to Microsoft Foundry Portal**
   - Go to: https://ai.azure.com
   - Sign in with your Azure account

2. **Create New Project**
   - Click "Create Project"
   - Name: `teams-moderation-project`
   - Select your Azure subscription and resource group
   - Choose region: `East US` or `West Europe` (recommended for best latency)

3. **Deploy a Model**
   - Go to "Model catalog"
   - Select `gpt-4o` or `gpt-4.1` (recommended for production)
   - Click "Deploy"
   - Deployment name: `gpt-4o-deployment`
   - Configure throughput (start with 10K tokens/min, adjust as needed)
   - Note your **Project Endpoint** (e.g., `https://<project-name>.<region>.api.azureml.ms`)

### Get Connection Details

```bash
# Note these values for your .env file:
# - FOUNDRY_PROJECT_ENDPOINT: Your project endpoint URL
# - FOUNDRY_MODEL_DEPLOYMENT: Your deployment name (e.g., "gpt-4o-deployment")
```

## 2. Azure AI Content Safety Setup

### Create Content Safety Resource

```bash
# Using Azure CLI
az cognitiveservices account create \
  --name teams-content-safety \
  --resource-group <your-rg> \
  --kind ContentSafety \
  --sku S0 \
  --location eastus \
  --yes

# Get endpoint and key
az cognitiveservices account show \
  --name teams-content-safety \
  --resource-group <your-rg> \
  --query "properties.endpoint" -o tsv

az cognitiveservices account keys list \
  --name teams-content-safety \
  --resource-group <your-rg> \
  --query "key1" -o tsv
```

### Or via Azure Portal

1. Go to Azure Portal → Create Resource
2. Search for "Content Safety"
3. Click Create
4. Configure:
   - Name: `teams-content-safety`
   - Pricing tier: `S0` (Standard)
   - Region: Same as your Foundry project
5. Note your **endpoint** and **key**

## 3. Microsoft Entra ID App Registration

### Create App Registration for Teams Access

1. **Navigate to Microsoft Entra ID**
   - Azure Portal → Microsoft Entra ID → App registrations → New registration

2. **Register Application**
   - Name: `Teams Moderation App`
   - Supported account types: "Single tenant"
   - Redirect URI: Leave blank
   - Click "Register"

3. **Note Application IDs**
   - Copy **Application (client) ID**
   - Copy **Directory (tenant) ID**

4. **Create Client Secret**
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Description: `Teams moderation secret`
   - Expiry: 24 months (or custom)
   - Click "Add"
   - **IMPORTANT**: Copy the secret value immediately (you won't see it again!)

5. **Configure API Permissions**
   - Go to "API permissions"
   - Click "Add a permission"
   - Select "Microsoft Graph"
   - Select "Application permissions" (not delegated)
   - Add these permissions:
     - `ChannelMessage.Read.All` - Read all channel messages
     - `ChannelMessage.Delete` - Delete channel messages
     - `Team.ReadBasic.All` - Read basic team info
     - `Channel.ReadBasic.All` - Read basic channel info
   - Click "Add permissions"

6. **Grant Admin Consent**
   - Click "Grant admin consent for [Your Organization]"
   - Confirm by clicking "Yes"
   - All permissions should now show green checkmarks

### Test Permissions

```bash
# Get access token
curl -X POST https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token \
  -d "client_id=<client-id>" \
  -d "client_secret=<client-secret>" \
  -d "scope=https://graph.microsoft.com/.default" \
  -d "grant_type=client_credentials"

# Test Teams access
curl -H "Authorization: Bearer <access-token>" \
  https://graph.microsoft.com/v1.0/teams/<team-id>/channels
```

## 4. Get Teams Team ID

### Find Your Team ID

**Method 1: Via Teams Web App**
1. Open Microsoft Teams in web browser
2. Navigate to your team
3. Look at the URL: `https://teams.microsoft.com/...groupId=<team-id>...`
4. Copy the `groupId` value

**Method 2: Via Graph Explorer**
1. Go to: https://developer.microsoft.com/graph/graph-explorer
2. Sign in
3. Run query: `GET https://graph.microsoft.com/v1.0/groups`
4. Find your team in the results

**Method 3: Via PowerShell**
```powershell
Install-Module -Name Microsoft.Graph
Connect-MgGraph -Scopes "Group.Read.All"
Get-MgGroup -Filter "resourceProvisioningOptions/Any(x:x eq 'Team')"
```

## 5. Azure Key Vault (Recommended for Production)

### Create Key Vault

```bash
az keyvault create \
  --name teams-mod-keyvault \
  --resource-group <your-rg> \
  --location eastus \
  --enable-rbac-authorization true

# Add secrets
az keyvault secret set \
  --vault-name teams-mod-keyvault \
  --name foundry-endpoint \
  --value "<your-foundry-endpoint>"

az keyvault secret set \
  --vault-name teams-mod-keyvault \
  --name teams-client-secret \
  --value "<your-client-secret>"

az keyvault secret set \
  --vault-name teams-mod-keyvault \
  --name content-safety-key \
  --value "<your-content-safety-key>"
```

### Grant Access to Managed Identity

```bash
# After deploying your app with managed identity
az keyvault set-policy \
  --name teams-mod-keyvault \
  --object-id <managed-identity-principal-id> \
  --secret-permissions get list
```

## 6. Configure Environment

Copy values to your `.env` file:

```bash
# Microsoft Foundry
FOUNDRY_PROJECT_ENDPOINT=https://<your-project>.<region>.api.azureml.ms
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o-deployment

# Azure AI Content Safety
CONTENT_SAFETY_ENDPOINT=https://<your-content-safety>.cognitiveservices.azure.com
CONTENT_SAFETY_KEY=<your-key>

# Microsoft Teams
TEAMS_TENANT_ID=<your-tenant-id>
TEAMS_CLIENT_ID=<your-client-id>
TEAMS_CLIENT_SECRET=<your-client-secret>
TEAMS_TEAM_ID=<your-team-id>

# Notifications
NOTIFICATION_EMAIL=hr@russellcellular.com
```

## 7. Verify Setup

Run the verification script:

```bash
python scripts/verify_setup.py
```

This will check:
- ✅ Microsoft Foundry connectivity
- ✅ Content Safety service access
- ✅ Teams Graph API permissions
- ✅ Model deployment availability

## Cost Estimates

### Monthly Cost Breakdown (Approximate)

| Service | Usage | Cost |
|---------|-------|------|
| Microsoft Foundry (gpt-4o) | 1M tokens/day | $110-220/mo |
| Azure Content Safety | 10K texts/day | $15-30/mo |
| Container Apps | 1 instance, 24/7 | $30-50/mo |
| Application Insights | Standard | $10-20/mo |
| **Total** | | **$165-320/mo** |

### Optimization Tips
- Use `gpt-4.1-mini` instead of `gpt-4o` for 80% cost reduction
- Implement caching for repeated content
- Batch Content Safety API calls
- Use consumption-based Container Apps

## Troubleshooting

### Common Issues

**"Unauthorized" when calling Graph API**
- Verify admin consent was granted
- Check app permissions are "Application" not "Delegated"
- Wait 5-10 minutes for permissions to propagate

**"Model not found" error**
- Verify deployment name matches exactly
- Check model is deployed (not just in catalog)
- Ensure endpoint URL is project endpoint, not Azure OpenAI

**Content Safety 429 errors**
- You're hitting rate limits
- Increase pricing tier or add retry logic
- Implement exponential backoff

## Next Steps

1. ✅ Complete this setup
2. Configure channel and policy settings (`config/`)
3. Test in dry-run mode
4. Deploy to Azure (see [DEPLOYMENT.md](DEPLOYMENT.md))
5. Monitor and tune policies

## Support

For setup assistance: it-support@russellcellular.com
