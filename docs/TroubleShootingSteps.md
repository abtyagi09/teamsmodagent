# 🛠️ Troubleshooting

When deploying Azure resources, you may encounter different error codes that stop or delay the deployment process. This section lists some of the most common errors along with possible causes and step-by-step resolutions.

Use these as quick reference guides to unblock your deployments.

## ⚡ Most Frequently Encountered Errors

| Error Code | Common Cause | Full Details |
|------------|--------------|--------------|
| **InsufficientQuota** | Not enough quota available in subscription | [View Solution](#quota--capacity-limitations) |
| **MissingSubscriptionRegistration** | Required feature not registered in subscription | [View Solution](#subscription--access-issues) |
| **ResourceGroupNotFound** | RG doesn't exist or using old .env file | [View Solution](#resource-group--deployment-management) |
| **DeploymentModelNotSupported** | Model not available in selected region | [View Solution](#regional--location-issues) |
| **ContainerAppStartupFailed** | Container configuration or permission issues | [View Solution](#container-app-issues) |

---

## 📖 Table of Contents

- [Subscription & Access Issues](#subscription--access-issues)
- [Quota & Capacity Limitations](#quota--capacity-limitations)
- [Resource Group & Deployment Management](#resource-group--deployment-management)
- [Regional & Location Issues](#regional--location-issues)
- [Container App Issues](#container-app-issues)
- [Configuration & Property Errors](#configuration--property-errors)
- [Teams Integration Issues](#teams-integration-issues)
- [Email Notification Issues](#email-notification-issues)

---

## Subscription & Access Issues

### MissingSubscriptionRegistration

**Error Message:**
```
The subscription is not registered to use namespace 'Microsoft.App'
```

**Cause:** Required Azure resource providers are not registered in your subscription.

**Resolution:**
```bash
# Register required resource providers
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.CognitiveServices
az provider register --namespace Microsoft.Communication

# Check registration status
az provider list --query "[?namespace=='Microsoft.App'].registrationState" -o table
```

### Insufficient Permissions

**Error Message:**
```
Authorization failed. The client does not have authorization to perform action
```

**Cause:** Your account lacks necessary permissions for resource creation.

**Resolution:**
1. **Check your role assignments:**
   ```bash
   az role assignment list --assignee $(az account show --query user.name -o tsv) --all
   ```

2. **Required roles:**
   - Contributor (resource creation)
   - User Access Administrator (role assignments)

3. **Request permissions from subscription owner if missing**

---

## Quota & Capacity Limitations

### InsufficientQuota

**Error Message:**
```
Operation could not be completed as it results in exceeding approved quota
```

**Cause:** Not enough quota for Azure OpenAI models or other services.

**Resolution:**

1. **Check current quota:**
   ```bash
   az cognitiveservices account list-usage \
     --name <your-openai-account> \
     --resource-group <your-resource-group>
   ```

2. **Request quota increase:**
   - Go to Azure Portal → Your OpenAI resource → Quotas
   - Click "Request quota increase"
   - Specify required tokens (default: 150k for GPT-4.1, 50k for GPT-4.1-mini)

3. **Try different region with available capacity:**
   ```bash
   azd down
   azd up  # Select different region when prompted
   ```

### Container App Quota Exceeded

**Error Message:**
```
Exceeded quota for Container Apps in region
```

**Resolution:**
1. **Try different region:**
   - East US 2
   - West US 2
   - North Central US

2. **Request Container Apps quota increase through Azure Portal**

---

## Resource Group & Deployment Management

### ResourceGroupNotFound

**Error Message:**
```
Resource group 'rg-teamschannelmod' could not be found
```

**Cause:** Resource group was deleted or deployment pointing to wrong RG.

**Resolution:**
```bash
# Check if resource group exists
az group list --query "[?name=='rg-teamschannelmod']" -o table

# If not found, azd will create it automatically on next deployment
azd up
```

### DeploymentNotFound

**Error Message:**
```
Deployment 'teamschannelmod' could not be found
```

**Resolution:**
```bash
# Clean up azd state and redeploy
azd down --purge
azd up
```

---

## Regional & Location Issues

### DeploymentModelNotSupported

**Error Message:**
```
The model 'gpt-4o-mini' is not supported in region 'westus'
```

**Cause:** Selected region doesn't support required AI models.

**Resolution:**
1. **Use recommended regions with OpenAI support:**
   - East US
   - East US 2
   - West US 2
   - North Central US

2. **Check model availability:**
   ```bash
   az cognitiveservices model list --location eastus2 --query "[?model.name=='gpt-4o-mini']"
   ```

3. **Redeploy with supported region:**
   ```bash
   azd down
   azd up  # Select supported region
   ```

---

## Container App Issues

### ContainerAppStartupFailed

**Error Message:**
```
Container app failed to start. Check application logs
```

**Cause:** Configuration errors, missing environment variables, or permission issues.

**Resolution:**

1. **Check container logs:**
   ```bash
   azd logs --service agent --tail 100
   azd logs --service ui --tail 100
   ```

2. **Verify environment variables:**
   ```bash
   az containerapp show --name ca-agent-<env-id> --resource-group <rg> \
     --query "properties.template.containers[0].env" -o table
   ```

3. **Check managed identity assignments:**
   ```bash
   # Verify identity has required roles
   az role assignment list --assignee <managed-identity-principal-id>
   ```

4. **Common missing roles:**
   ```bash
   # Add missing role assignments
   az role assignment create \
     --assignee <managed-identity-principal-id> \
     --role "Cognitive Services User" \
     --scope <content-safety-resource-id>
   
   az role assignment create \
     --assignee <managed-identity-principal-id> \
     --role "Azure AI User" \
     --scope <ai-foundry-resource-id>
   ```

### Container Image Pull Failures

**Error Message:**
```
Failed to pull container image
```

**Resolution:**
```bash
# Check container registry access
az acr login --name <your-acr-name>

# Verify image exists
az acr repository list --name <your-acr-name> -o table

# Rebuild and push images
azd deploy
```

---

## Configuration & Property Errors

### App Configuration Connection Failures

**Error Message:**
```
Unable to connect to Azure App Configuration
```

**Cause:** Incorrect connection string or missing permissions.

**Resolution:**
1. **Verify App Configuration exists:**
   ```bash
   az appconfig list --resource-group <your-rg> -o table
   ```

2. **Check connection string:**
   ```bash
   az appconfig credential list --name <appconfig-name> --resource-group <rg>
   ```

3. **Verify managed identity has access:**
   ```bash
   az role assignment create \
     --assignee <managed-identity-principal-id> \
     --role "App Configuration Data Owner" \
     --scope <app-config-resource-id>
   ```

---

## Teams Integration Issues

### Teams Authentication Failures

**Error Message:**
```
AADSTS70011: The provided value for the input parameter 'scope' is not valid
```

**Cause:** Incorrect Teams app registration configuration.

**Resolution:**
1. **Verify Azure AD App Registration:**
   - Go to Azure Portal → Azure Active Directory → App registrations
   - Find your Teams app registration
   - Check API permissions include Microsoft Graph

2. **Required API permissions:**
   - `Channel.ReadBasic.All`
   - `ChannelMessage.Read.All`
   - `Team.ReadBasic.All`

3. **Update environment variables:**
   ```env
   TEAMS_TENANT_ID=your-tenant-id
   TEAMS_CLIENT_ID=your-app-client-id
   TEAMS_CLIENT_SECRET=your-app-secret
   ```

### Teams Channel Not Found

**Error Message:**
```
Channel not found or access denied
```

**Resolution:**
1. **Verify Team ID is correct:**
   ```bash
   # Get Teams info using Microsoft Graph Explorer
   # https://developer.microsoft.com/en-us/graph/graph-explorer
   ```

2. **Check app permissions in Teams:**
   - Teams app must be installed in the target team
   - App must have permission to read channel messages

---

## Azure Communication Services Issues

### Email Configuration Problems

#### Connection String Authentication Failed

**Error Messages:**
```
Authentication failed for Azure Communication Services
Failed to authenticate with Azure Communication Services
Invalid connection string format
```

**Resolution:**
1. **Verify Connection String Format:**
   ```bash
   # Get correct connection string
   az communication list-key \
     --name "acs-xcpeyeriwqbc4" \
     --resource-group rg-azdteamsmod2 \
     --query "primaryConnectionString" -o tsv
   
   # Should look like: endpoint=https://acs-name.communication.azure.com/;accesskey=ACCESS_KEY
   ```

2. **Update Environment Variable:**
   ```bash
   azd env set EMAIL_CONNECTION_STRING "your-correct-connection-string"
   azd up  # Redeploy to apply changes
   ```

3. **Verify ACS Resource Status:**
   ```bash
   az communication show --name "acs-xcpeyeriwqbc4" --resource-group rg-azdteamsmod2
   ```

#### Domain Not Verified or Missing

**Error Messages:**
```
Domain not found or not verified
Sender domain verification failed
Invalid sender email domain
```

**Resolution:**
1. **Check Domain Status:**
   ```bash
   # List configured domains
   az communication email domain list \
     --email-service-name "ecs-xcpeyeriwqbc4" \
     --resource-group rg-azdteamsmod2
   
   # Check domain verification status
   az communication email domain show \
     --domain-name "your-domain" \
     --email-service-name "ecs-xcpeyeriwqbc4" \
     --resource-group rg-azdteamsmod2
   ```

2. **Add Azure-Managed Domain (Quick Fix):**
   ```bash
   # Create Azure-managed domain for testing
   az communication email domain create \
     --domain-management AzureManaged \
     --location Global \
     --email-service-name "ecs-xcpeyeriwqbc4" \
     --resource-group rg-azdteamsmod2
   ```

3. **Update Sender Email:**
   ```bash
   # Use the Azure-managed domain
   azd env set EMAIL_SENDER "noreply@{generated-domain}.azurecomm.net"
   azd up
   ```

#### Email Delivery Failures

**Error Messages:**
```
Email delivery failed
Recipient address rejected
Rate limit exceeded
```

**Resolution:**
1. **Check Email Limits:**
   ```bash
   # Monitor email usage
   az monitor metrics list \
     --resource "/subscriptions/{sub-id}/resourceGroups/rg-azdteamsmod2/providers/Microsoft.Communication/CommunicationServices/acs-xcpeyeriwqbc4" \
     --metric "EmailDeliveryAttempts,EmailDeliveryFailures"
   ```

2. **Verify Recipient Addresses:**
   - Ensure recipient emails are valid
   - Check if emails are going to spam folder
   - Verify recipient domain accepts external emails

3. **Check Rate Limits:**
   - Free tier: 100 emails/month
   - Standard tier: Rate limits per domain
   - Implement email batching if hitting limits

4. **Test Email Sending:**
   ```python
   # Test script to validate email functionality
   from azure.communication.email import EmailClient
   import os
   
   connection_string = os.environ.get('EMAIL_CONNECTION_STRING')
   sender_email = os.environ.get('EMAIL_SENDER')
   
   client = EmailClient.from_connection_string(connection_string)
   
   message = {
       "senderAddress": sender_email,
       "recipients": {"to": [{"address": "test@example.com"}]},
       "content": {
           "subject": "Test Email",
           "plainText": "Test message from Teams moderation system"
       }
   }
   
   try:
       poller = client.begin_send(message)
       result = poller.result()
       print(f"Email sent successfully: {result.message_id}")
   except Exception as e:
       print(f"Email send failed: {str(e)}")
   ```

### Email Template and Formatting Issues

#### HTML Content Not Rendering

**Problem:** Email appears as plain text instead of formatted HTML.

**Resolution:**
1. **Verify HTML Content Type:**
   - Ensure email template includes both HTML and plain text versions
   - Check Content-Type headers in email configuration

2. **Test HTML Templates:**
   ```bash
   # Access UI dashboard → Email Templates
   # Test different template formats
   # Verify HTML syntax is correct
   ```

#### Missing Template Variables

**Problem:** Email contains `{{variable_name}}` instead of actual values.

**Resolution:**
1. **Check Variable Mapping:**
   - Verify all template variables are defined in code
   - Check variable names match exactly (case-sensitive)

2. **Available Variables:**
   ```
   {{violation_type}} - Type of content violation
   {{severity}} - Violation severity level  
   {{author}} - Message author information
   {{channel}} - Teams channel name
   {{message_content}} - Original message text
   {{timestamp}} - When violation occurred
   {{action_taken}} - Action performed by system
   ```

### Performance and Scaling Issues

#### Email Sending Delays

**Problem:** Long delays between violation detection and email delivery.

**Resolution:**
1. **Check Email Queue Status:**
   ```bash
   # Monitor email sending performance
   azd logs --service agent --tail 100 | grep -i "email\|notification"
   ```

2. **Optimize Email Batching:**
   - Configure email batching for multiple violations
   - Implement async email sending
   - Add retry logic for failed sends

3. **Scale Email Processing:**
   ```bash
   # Increase container resources if needed
   az containerapp update \
     --name ca-agent-xcpeyeriwqbc4 \
     --resource-group rg-azdteamsmod2 \
     --cpu 0.5 \
     --memory 1.0Gi
   ```

## Email Notification Issues

### Communication Services Authentication Failed

**Error Message:**
```
Authentication failed for Azure Communication Services
```

**Cause:** Incorrect connection string or missing sender domain verification.

**Resolution:**
1. **Verify connection string:**
   ```bash
   az communication list --resource-group <rg> -o table
   az communication list-key --name <acs-name> --resource-group <rg>
   ```

2. **Check sender email domain:**
   - Must be from verified Azure Communication Services domain
   - Format: `noreply@<your-domain>.azurecomm.net`

3. **Test email configuration:**
   ```bash
   python tests/test_email.py
   ```

### Email Delivery Failures

**Error Message:**
```
Email delivery failed - recipient rejected
```

**Resolution:**
1. **Check recipient email validity**
2. **Verify sender domain is not blocked**
3. **Review Azure Communication Services logs**
4. **Test with different recipient email**

---

## General Troubleshooting Steps

### Check Deployment Status

```bash
# View current deployment status
azd env get-values

# Check resource group resources
az resource list --resource-group <your-rg> --output table

# View deployment history
az deployment group list --resource-group <your-rg> --output table
```

### Clean Deployment

```bash
# Complete cleanup and redeploy
azd down --purge
azd up
```

### Enable Debug Logging

```bash
# Run with debug output
azd up --debug

# Check application logs
azd logs --service agent --follow
azd logs --service ui --follow
```

---

## Additional Resources

- [Azure Resource Manager troubleshooting](https://learn.microsoft.com/en-us/azure/azure-resource-manager/troubleshooting/)
- [Container Apps troubleshooting](https://learn.microsoft.com/en-us/azure/container-apps/troubleshooting)
- [Azure OpenAI troubleshooting](https://learn.microsoft.com/en-us/azure/ai-services/openai/troubleshooting)

---

## Need Additional Help?

If you continue to experience issues:

1. **Check Azure Status:** [Azure Status Page](https://status.azure.com/)
2. **Review Documentation:** Ensure following latest deployment guide
3. **Contact Support:** Reach out to your system administrator with error details and logs