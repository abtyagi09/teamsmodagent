# Next Steps after Deployment

This document provides guidance on the next steps after successfully deploying the Teams Channel Moderation solution.

## Table of Contents

1. [Next Steps](#next-steps)
2. [What was deployed](#what-was-deployed)
3. [Configuration](#configuration)
4. [Troubleshooting](#troubleshooting)

---

## Next Steps

### 1. Configure Moderation Policies

Access your UI dashboard and set up content moderation rules:

**Policy Configuration:**
- **Hate Speech Detection**: Set sensitivity levels for hate speech detection
- **Harassment Detection**: Configure bullying and intimidation thresholds
- **Profanity Filter**: Define inappropriate language handling
- **Violence/Self-harm**: Set detection parameters for violent content
- **PII Detection**: Configure personal information detection rules

**Action Configuration:**
- **Monitor Mode**: Log violations without taking action
- **Flag Mode**: Mark violating content for review
- **Delete Mode**: Automatically remove violating content
- **Notify Mode**: Send email alerts for violations

### 2. Set Up Teams Integration

**📋 Complete Setup Guide:** For detailed step-by-step instructions, see [Teams Entra ID Setup Guide](docs/TEAMS_ENTRA_SETUP.md)

**Quick Overview:** Configure your Microsoft Teams connection through Entra ID (Azure Active Directory):

#### 2.1 Create Entra ID App Registration

1. **Navigate to Entra ID:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Search for and select "Entra ID" or "Azure Active Directory"
   - Select "App registrations" from the left menu

2. **Create New App Registration:**
   ```
   Name: Teams Channel Moderation Bot
   Supported account types: Accounts in this organizational directory only
   Redirect URI: Leave empty for now
   ```

3. **Note the Application Details:**
   - Copy the **Application (client) ID** - you'll need this for TEAMS_CLIENT_ID
   - Copy the **Directory (tenant) ID** - you'll need this for TEAMS_TENANT_ID

#### 2.2 Configure API Permissions

1. **Go to API Permissions:**
   - Select your app registration
   - Click "API permissions" in the left menu

2. **Add Microsoft Graph Permissions:**
   Click "Add a permission" → "Microsoft Graph" → "Application permissions"
   
   **Required Permissions:**
   - `Channel.ReadBasic.All` - Read basic channel properties
   - `ChannelMessage.Read.All` - Read all channel messages
   - `Team.ReadBasic.All` - Read basic team properties
   - `TeamsAppInstallation.Read.All` - Read Teams app installations
   - `User.Read.All` - Read user profiles

3. **Grant Admin Consent:**
   - Click "Grant admin consent for [Your Organization]"
   - Confirm the consent grant

#### 2.3 Create Client Secret

1. **Go to Certificates & Secrets:**
   - Select "Certificates & secrets" from left menu
   - Click "New client secret"

2. **Create Secret:**
   ```
   Description: Teams Moderation Bot Secret
   Expires: Choose appropriate expiration (12-24 months recommended)
   ```

3. **Copy Secret Value:**
   - **IMPORTANT:** Copy the secret VALUE immediately (not the ID)
   - You'll need this for TEAMS_CLIENT_SECRET
   - Store securely - you cannot retrieve this value again

#### 2.4 Find Your Teams Information

1. **Get Team ID:**
   - Open Microsoft Teams
   - Navigate to your team
   - Click the three dots (...) next to team name
   - Select "Get link to team"
   - Copy the URL and extract the Team ID from the URL:
     ```
     https://teams.microsoft.com/l/team/19%3A[TEAM-ID]%40thread.tacv2/conversations?groupId=[GROUP-ID]
     ```

2. **Alternative Method using PowerShell:**
   ```powershell
   # Install Microsoft Teams PowerShell module
   Install-Module -Name MicrosoftTeams -Force
   
   # Connect to Teams
   Connect-MicrosoftTeams
   
   # List all teams
   Get-Team
   
   # Get specific team details
   Get-Team -DisplayName "Your Team Name"
   ```

#### 2.5 Configure Application Settings

Update your application configuration with the collected values:

**Environment Variables:**
- `TEAMS_TENANT_ID`: Directory (tenant) ID from step 2.1
- `TEAMS_CLIENT_ID`: Application (client) ID from step 2.1  
- `TEAMS_CLIENT_SECRET`: Secret value from step 2.3
- `TEAMS_TEAM_ID`: Team ID from step 2.4

**Channel Selection:**
- Select specific channels to monitor
- Exclude private or sensitive channels (e.g., HR, executive channels)  
- Configure monitoring frequency (default: 60 seconds)

#### 2.6 Deploy Configuration

After collecting all the required values, update your deployment:

1. **Update Environment Variables:**
   ```bash
   # Set the Teams configuration values
   azd env set TEAMS_TENANT_ID "your-tenant-id"
   azd env set TEAMS_CLIENT_ID "your-client-id" 
   azd env set TEAMS_CLIENT_SECRET "your-client-secret"
   azd env set TEAMS_TEAM_ID "your-team-id"
   
   # Redeploy to apply changes
   azd up
   ```

2. **Verify Configuration in UI:**
   - Access the UI dashboard
   - Navigate to Teams configuration section
   - Verify all values are correctly populated
   - Test Teams connection

#### 2.7 Security Considerations

**App Registration Security:**
- Rotate client secrets regularly (every 12-24 months)
- Use minimum required permissions (principle of least privilege)
- Enable conditional access policies for the app if available
- Monitor app usage through Azure AD audit logs

**Permission Monitoring:**
- Regularly review granted permissions
- Remove unused permissions
- Monitor for permission escalation requests
- Document approved permission changes

**Access Control:**
- Limit who can manage the app registration
- Use Azure AD privileged identity management (PIM) for admin access
- Enable multi-factor authentication for administrators
- Regular access reviews for app owners

### 3. Configure Email Notifications

Set up Azure Communication Services for email alerts:

**Email Configuration:**
- Verify sender domain in Azure Communication Services
- Configure recipient email addresses for alerts
- Set up email templates for different violation types
- Test email delivery functionality

### 4. Monitor and Tune

**Monitor Operations:**
```bash
# View agent logs
azd logs --service agent --follow

# View UI logs  
azd logs --service ui --follow

# Check container app status
az containerapp show --name <app-name> --resource-group <rg> --query "properties.provisioningState"
```

**Tune Policies:**
- Review detected violations in the UI dashboard
- Adjust sensitivity levels to reduce false positives
- Add custom keywords to policy filters
- Monitor notification frequency and adjust as needed

---

## What was deployed

### Infrastructure configuration

The deployment created the following Azure resources:

```yaml
- azure.yaml                    # azd project configuration
- infra/                        # Infrastructure-as-code Bicep files
  - main.bicep                  # Main infrastructure template
  - core/                       # Core service modules
    - host/
      - container-app.bicep     # Container Apps configuration
      - container-registry.bicep # Container Registry
    - ai/
      - ai-foundry.bicep        # AI Foundry project
    - communication/
      - communication-service.bicep # Email services
    - config/
      - app-configuration.bicep # Configuration storage
    - messaging/
      - service-bus.bicep       # Message queuing
```

The resources declared in [main.bicep](../infra/main.bicep) are provisioned when running `azd up` or `azd provision`.

### Azure Resources Created

- **Azure Container App** to host the moderation agent service
- **Azure Container App** to host the UI dashboard service  
- **Azure Container Registry** to store container images
- **Azure AI Foundry Project** for AI model deployments
- **Azure Content Safety** service for content moderation
- **Azure Communication Services** for email notifications
- **Azure App Configuration** for storing application settings
- **Azure Service Bus** for reliable message processing
- **Managed Identity** for secure authentication between services

### Build from source

The deployment builds container images from source code using:

**Agent Service:**
- Source: `src/` directory
- Dockerfile: `Dockerfile.agent`
- Exposed on internal port for service communication

**UI Service:**
- Source: `ui/` directory  
- Dockerfile: `Dockerfile.ui`
- Exposed on public endpoint for web access

**Build Process:**
1. `azd package` - Builds container images from source
2. `azd provision` - Creates Azure infrastructure 
3. `azd deploy` - Pushes images and deploys containers

More information about [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/).

---

## Configuration

### Environment Variables

The following environment variables are configured automatically during deployment:

**AI Services:**
- `FOUNDRY_PROJECT_ENDPOINT` - Azure AI Foundry endpoint
- `FOUNDRY_MODEL_DEPLOYMENT` - Deployed model name
- `CONTENT_SAFETY_ENDPOINT` - Content Safety service endpoint
- `CONTENT_SAFETY_KEY` - Content Safety API key

**Teams Integration:**
- `TEAMS_TENANT_ID` - Azure AD tenant ID
- `TEAMS_CLIENT_ID` - Teams app registration client ID
- `TEAMS_CLIENT_SECRET` - Teams app registration secret
- `TEAMS_TEAM_ID` - Target Teams team ID

**Communication Services:**
- `EMAIL_CONNECTION_STRING` - Azure Communication Services connection
- `EMAIL_SENDER` - Verified sender email address
- `NOTIFICATION_EMAIL` - Recipient for violation alerts

**Configuration Storage:**
- `CONFIG_CONNECTION_STRING` - Azure App Configuration connection

### Custom Configuration

Modify settings through the UI dashboard or by updating Azure App Configuration directly:

**Policy Customization:**
- Adjust detection thresholds for each content type
- Add custom keywords or phrases to monitor
- Configure response actions per policy type
- Set up escalation rules for repeated violations

**Channel Management:**
- Add/remove monitored channels
- Set channel-specific policies
- Configure monitoring schedules
- Exclude specific users or bots from monitoring

---

## Troubleshooting

### Check Deployment Status

```bash
# View deployment details
azd env get-values

# Check resource group status
az resource list --resource-group <resource-group-name> --output table

# Verify container apps are running
az containerapp list --resource-group <resource-group-name> --output table
```

### Common Issues

**Agent not processing messages:**
1. Check managed identity has required permissions
2. Verify Teams app registration configuration
3. Ensure policies are saved in Azure App Configuration
4. Review agent logs for authentication errors

**Email notifications not working:**
1. Verify Azure Communication Services sender domain
2. Check recipient email addresses are correct  
3. Test email connectivity from Azure portal
4. Review notification service logs

**UI dashboard not accessible:**
1. Check container app public endpoint configuration
2. Verify UI container is running successfully
3. Review firewall and network security group rules
4. Check for any SSL certificate issues

### Debug Commands

```bash
# View live logs from services
azd logs --service agent --follow
azd logs --service ui --follow

# Check container app health
az containerapp show --name <agent-app-name> --resource-group <rg> \
  --query "properties.latestRevision.healthState"

# Review recent deployments
az deployment group list --resource-group <rg> --output table

# Test email functionality
python scripts/test_email.py

# Verify Teams connectivity  
python scripts/test_teams_connection.py
```

### Performance Tuning

**Scaling Configuration:**
- Adjust container app scaling rules based on Teams usage
- Configure appropriate CPU and memory limits
- Set up auto-scaling triggers for high message volumes

**Monitoring Setup:**
- Enable Application Insights for detailed telemetry
- Set up alerts for service health and error rates
- Configure log analytics for advanced querying

### Additional information

For additional information about setting up your `azd` project, visit our official [Azure Developer CLI docs](https://learn.microsoft.com/azure/developer/azure-developer-cli/make-azd-compatible?pivots=azd-convert).

**Related Documentation:**
- [Deployment Guide](docs/DeploymentGuide.md) - Complete deployment instructions
- [Local Development Setup](docs/LocalDevelopmentSetup.md) - Development environment setup
- [Configuration Architecture](docs/CONFIGURATION_ARCHITECTURE.md) - Detailed configuration guide
- [Troubleshooting Steps](docs/TroubleShootingSteps.md) - Comprehensive troubleshooting guide