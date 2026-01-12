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

### 3. Configure Azure Communication Services for Email Notifications

**📋 Complete Setup Guide:** See [Email Setup Guide](docs/EMAIL_SETUP.md) for detailed instructions.

**Quick Overview:** Configure Azure Communication Services for email alerts and notifications:

#### 3.1 Create Azure Communication Services Resources

The infrastructure deployment automatically creates ACS resources, but you need to configure domains:

1. **Verify ACS Resources Created:**
   ```bash
   # Check if ACS resources were created by deployment
   az resource list --resource-group rg-azdteamsmod2 --resource-type Microsoft.Communication/CommunicationServices
   az resource list --resource-group rg-azdteamsmod2 --resource-type Microsoft.Communication/EmailServices
   ```

2. **Configure Email Domain:**
   - **Option A (Quick Start):** Use Azure-managed domain for testing
   - **Option B (Production):** Configure your custom domain with DNS verification

#### 3.2 Azure-Managed Domain Setup (Recommended for Testing)

1. **Access Azure Portal:**
   - Navigate to Azure Communication Services → Email Communication Services
   - Select your email service resource

2. **Add Azure Subdomain:**
   - Click "Provision domains" → "Add domain" → "Azure subdomain"
   - Azure creates: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.azurecomm.net`
   - Domain is pre-verified and ready to use immediately

3. **Link Domain to ACS:**
   ```bash
   # Get your email service name
   az communication email list --resource-group rg-azdteamsmod2
   
   # Link the Azure-managed domain
   az communication email domain link \
     --email-service-name "ecs-xcpeyeriwqbc4" \
     --domain-name "your-azure-domain.azurecomm.net" \
     --resource-group rg-azdteamsmod2
   ```

#### 3.3 Custom Domain Setup (Production)

1. **Add Custom Domain:**
   - In Email Communication Services, click "Add domain" → "Custom domain"
   - Enter your domain (e.g., `yourcompany.com`)

2. **Configure DNS Records:**
   - Add required TXT record for domain verification
   - Add CNAME records for email authentication (SPF, DKIM)
   - Wait for verification (15 minutes to 48 hours)

3. **Link Custom Domain:**
   ```bash
   az communication email domain link \
     --email-service-name "ecs-xcpeyeriwqbc4" \
     --domain-name "yourcompany.com" \
     --resource-group rg-azdteamsmod2
   ```

#### 3.4 Configure Email Settings

1. **Get Connection String:**
   ```bash
   # Get ACS connection string
   az communication list-key \
     --name "acs-xcpeyeriwqbc4" \
     --resource-group rg-azdteamsmod2 \
     --query "primaryConnectionString" -o tsv
   ```

2. **Update Environment Variables:**
   ```bash
   # Set email configuration
   azd env set EMAIL_CONNECTION_STRING "endpoint=https://acs-xcpeyeriwqbc4.communication.azure.com/;accesskey=YOUR_ACCESS_KEY"
   azd env set EMAIL_SENDER "noreply@your-domain.azurecomm.net"
   azd env set NOTIFICATION_EMAIL "admin@yourcompany.com"
   
   # Redeploy to apply changes
   azd up
   ```

#### 3.5 Test Email Functionality

1. **Test Through UI Dashboard:**
   - Access the UI dashboard
   - Navigate to "Email Configuration" section
   - Click "Send Test Email"
   - Verify email delivery to configured recipients

2. **Test via Azure Portal:**
   - Go to Communication Services → Email Communication Services
   - Use "Send test email" feature
   - Verify email templates and delivery

#### 3.6 Configure Email Templates

Customize email notifications for different violation types:

**Template Types:**
- **Hate Speech Detection**: High-priority immediate alerts
- **Harassment/Bullying**: Medium-priority with context
- **PII Detection**: Privacy-focused notifications
- **Policy Violations**: General content policy alerts

**Email Recipients:**
- IT administrators
- HR representatives
- Team moderators
- Compliance officers

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

## Post-Deployment Verification

### 5. Complete System Verification

After completing the Teams and email configuration, verify the entire system is working:

#### 5.1 Infrastructure Health Check

```bash
# Check all Azure resources status
az resource list --resource-group rg-azdteamsmod2 --query "[].{name:name, type:type, location:location, provisioningState:properties.provisioningState}" --output table

# Verify container apps are running
az containerapp list --resource-group rg-azdteamsmod2 --query "[].{name:name, status:properties.provisioningState, replicas:properties.runningState}" --output table

# Check managed identity assignments
az role assignment list --assignee $(az identity show --name "id-xcpeyeriwqbc4" --resource-group rg-azdteamsmod2 --query principalId -o tsv) --output table
```

#### 5.2 Application Configuration Verification

```bash
# Check environment variables are set correctly
azd env list

# Verify agent startup and configuration loading
azd logs --service agent --tail 100 | grep -i "Starting Teams moderation\|Connected to Azure\|Monitoring configured channels"

# Check UI accessibility
curl -I $(azd show --query services.ui.uri -o tsv)
```

#### 5.3 Teams Integration Testing

1. **Test Teams Connection:**
   ```bash
   # Monitor logs for Teams API calls
   azd logs --service agent --follow &
   
   # Post a test message in monitored channel
   # Watch logs for message processing
   ```

2. **Verify Channel Detection:**
   - Access UI dashboard → Teams Configuration
   - Verify correct team and channels are detected
   - Check monitoring status is "Active"

#### 5.4 Email Notification Testing

1. **Test Email Delivery:**
   - Navigate to UI dashboard → Email Test
   - Send test email and verify delivery
   - Check email formatting and content

2. **End-to-End Test:**
   - Post a message with policy-violating content in monitored channel
   - Verify message is detected and processed
   - Confirm email notification is sent
   - Check appropriate action was taken (flag/delete based on configuration)

### 6. Ongoing Operations and Monitoring

#### 6.1 Daily Monitoring Tasks

**Health Check Commands:**
```bash
# Daily health check script
#!/bin/bash
echo "=== Daily Teams Moderation Health Check ==="
echo "Date: $(date)"

# Check container app status
echo -e "\n1. Container App Status:"
az containerapp show --name ca-agent-xcpeyeriwqbc4 --resource-group rg-azdteamsmod2 --query "properties.runningState" -o tsv

# Check recent log errors
echo -e "\n2. Recent Errors (last 1 hour):"
azd logs --service agent --tail 500 | grep -i "error\|exception\|failed" | tail -10

# Check message processing volume
echo -e "\n3. Message Processing (last hour):"
azd logs --service agent --tail 1000 | grep "Processed message" | tail -5

# Check email delivery status
echo -e "\n4. Email Notifications (last 24h):"
azd logs --service agent --tail 2000 | grep "Notification sent" | tail -5
```

#### 6.2 Weekly Maintenance Tasks

1. **Review Detection Accuracy:**
   - Access UI dashboard → Analytics
   - Review false positive/negative rates
   - Adjust policy sensitivity if needed

2. **User Access Review:**
   - Review Teams channel membership changes
   - Update monitoring channel list if needed
   - Verify notification recipient list is current

3. **Performance Review:**
   ```bash
   # Check container resource usage
   az monitor metrics list \
     --resource "/subscriptions/{subscription-id}/resourceGroups/rg-azdteamsmod2/providers/Microsoft.App/containerApps/ca-agent-xcpeyeriwqbc4" \
     --metric "CpuPercentage,MemoryPercentage" \
     --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
   ```

#### 6.3 Monthly Security Review

1. **Credential Rotation:**
   - Check Teams client secret expiration date
   - Rotate secrets if approaching expiration (90 days before)
   - Update ACS connection strings if needed

2. **Access Review:**
   - Review Entra ID app registration permissions
   - Audit email notification recipients
   - Check Azure resource access permissions

3. **Compliance Check:**
   - Review processed violations and actions taken
   - Generate compliance reports from UI dashboard
   - Document any policy adjustments made

### 7. Scaling and Performance Optimization

#### 7.1 Container Scaling Configuration

```bash
# Update container app scaling rules
az containerapp update \
  --name ca-agent-xcpeyeriwqbc4 \
  --resource-group rg-azdteamsmod2 \
  --min-replicas 1 \
  --max-replicas 5 \
  --scale-rule-name "cpu-scale" \
  --scale-rule-type "cpu" \
  --scale-rule-metadata "targetUtilization=70"

# Add memory-based scaling
az containerapp update \
  --name ca-agent-xcpeyeriwqbc4 \
  --resource-group rg-azdteamsmod2 \
  --scale-rule-name "memory-scale" \
  --scale-rule-type "memory" \
  --scale-rule-metadata "targetUtilization=80"
```

#### 7.2 Performance Monitoring

1. **Set Up Application Insights Alerts:**
   ```bash
   # Alert for high error rate
   az monitor metrics alert create \
     --name "TeamsModeration-ErrorRate" \
     --resource-group rg-azdteamsmod2 \
     --scopes "/subscriptions/{subscription-id}/resourceGroups/rg-azdteamsmod2/providers/microsoft.insights/components/appi-xcpeyeriwqbc4" \
     --condition "avg exceptions/count > 5" \
     --description "High error rate in Teams moderation agent"
   
   # Alert for response time
   az monitor metrics alert create \
     --name "TeamsModeration-ResponseTime" \
     --resource-group rg-azdteamsmod2 \
     --scopes "/subscriptions/{subscription-id}/resourceGroups/rg-azdteamsmod2/providers/microsoft.insights/components/appi-xcpeyeriwqbc4" \
     --condition "avg requests/duration > 5000" \
     --description "High response time in Teams moderation system"
   ```

2. **Performance Tuning Guidelines:**
   - **Message Processing**: Adjust polling interval based on team activity
   - **AI Model Calls**: Optimize batch processing for better throughput  
   - **Email Delivery**: Implement batching for high-volume notifications
   - **Resource Allocation**: Monitor and adjust CPU/memory based on usage patterns

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