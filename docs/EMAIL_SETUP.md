# Email Notification Setup

This guide explains how to configure email notifications for Teams moderation alerts using Azure Communication Services (ACS) Email.

## Prerequisites

- Azure subscription
- Azure Communication Services resource
- Verified email domain (or use Azure-managed domain for testing)

## Setup Steps

### 1. Create Azure Communication Services Resource

```bash
# Create ACS resource
az communication create \
  --name "teams-mod-email" \
  --resource-group "teams-mod-rg" \
  --location "global" \
  --data-location "United States"
```

### 2. Create Email Communication Service

```bash
# Create Email Communication Service
az communication email create \
  --name "teams-mod-email-svc" \
  --resource-group "teams-mod-rg" \
  --location "global" \
  --data-location "United States"
```

### 3. Configure Email Domain

**Option A: Use Azure Managed Domain (Quick Start)**

1. Go to Azure Portal → Communication Services → Email Communication Services
2. Select your email service
3. Click "Provision domains" → "Add domain" → "Azure subdomain"
4. Azure will create a domain like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.azurecomm.net`
5. This domain is pre-verified and ready to use

**Option B: Use Custom Domain (Production)**

1. Go to Azure Portal → Communication Services → Email Communication Services
2. Click "Provision domains" → "Add domain" → "Custom domain"
3. Enter your domain (e.g., `yourdomain.com`)
4. Add the required DNS records (TXT, CNAME) to your domain registrar
5. Wait for verification (can take 15 minutes to 48 hours)

### 4. Link Email Domain to Communication Service

```bash
# Link the email domain
az communication email domain link \
  --email-service-name "teams-mod-email-svc" \
  --domain-name "your-domain-name" \
  --resource-group "teams-mod-rg"
```

### 5. Get Connection String

```bash
# Get primary connection string
az communication list-key \
  --name "teams-mod-email" \
  --resource-group "teams-mod-rg" \
  --query "primaryConnectionString" -o tsv
```

Copy the connection string output.

### 6. Configure Environment Variables

Add to your `.env` file:

```env
# Azure Communication Services Email Configuration
EMAIL_CONNECTION_STRING=endpoint=https://teams-mod-email.communication.azure.com/;accesskey=YOUR_ACCESS_KEY

# Sender email (use the domain you configured)
EMAIL_SENDER=DoNotReply@xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.azurecomm.net
```

For custom domain:
```env
EMAIL_SENDER=noreply@yourdomain.com
```

### 7. Deploy Configuration

Update your azd environment with the email configuration:

```bash
# Set email environment variables
azd env set EMAIL_CONNECTION_STRING "endpoint=https://your-acs-resource.communication.azure.com/;accesskey=YOUR_ACCESS_KEY"
azd env set EMAIL_SENDER "noreply@your-domain.azurecomm.net"
azd env set NOTIFICATION_EMAIL "admin@yourcompany.com"

# Redeploy application with email configuration
azd up
```

### 8. Test Email Sending

#### Method 1: Test Through UI Dashboard

1. **Access the UI Dashboard** (URL provided by `azd up`)
2. **Navigate to Email Configuration** section
3. **Click "Send Test Email"** button
4. **Verify email delivery** to configured recipients

#### Method 2: Test via Azure Portal

1. **Go to Azure Portal** → Communication Services → Email Communication Services
2. **Select your email service**
3. **Use "Send test email"** feature
4. **Configure test email:**
   ```
   To: your-test-email@domain.com
   From: noreply@your-domain.azurecomm.net
   Subject: Teams Moderation Test
   Body: This is a test email from Teams Channel Moderation system.
   ```

#### Method 3: Test Programmatically

```python
# Test script - save as test_email.py
from azure.communication.email import EmailClient
import os

connection_string = os.environ.get('EMAIL_CONNECTION_STRING')
sender_email = os.environ.get('EMAIL_SENDER')
recipient_email = os.environ.get('NOTIFICATION_EMAIL')

client = EmailClient.from_connection_string(connection_string)

message = {
    "senderAddress": sender_email,
    "recipients": {
        "to": [{"address": recipient_email}]
    },
    "content": {
        "subject": "Teams Moderation System - Test Email",
        "plainText": "This is a test email from the Teams Channel Moderation system. If you receive this, email notifications are working correctly.",
        "html": """
        <h2>Teams Moderation System Test</h2>
        <p>This is a test email from the Teams Channel Moderation system.</p>
        <p>If you receive this, email notifications are working correctly.</p>
        <hr>
        <small>Sent from Azure Communication Services</small>
        """
    }
}

try:
    poller = client.begin_send(message)
    result = poller.result()
    print(f"Email sent successfully. Message ID: {result.message_id}")
except Exception as e:
    print(f"Failed to send email: {str(e)}")

message = {
    "senderAddress": "DoNotReply@yourdomain.com",
    "recipients": {
        "to": [{"address": "test@example.com"}],
    },
    "content": {
        "subject": "Test Email",
        "plainText": "This is a test email from Teams Moderation System",
    },
}

poller = client.begin_send(message)
result = poller.result()
print(f"Email sent! Message ID: {result.message_id}")
```

## Email Limits

### Free Tier
- 100 emails/month
- Good for testing

### Standard Tier (Pay-as-you-go)
- $0.00025 per email
- Volume discounts available
- Rate limits: 
  - 60 emails/minute per domain
  - 1,000 emails/hour per domain

## Email Template

The system sends HTML-formatted emails with:
- Color-coded severity indicators (🔴 High, 🟡 Medium, 🟢 Low)
- Violation details (policy, author, channel, timestamp)
- Action taken (deleted, flagged)
- Recommended follow-up actions
- Professional formatting

## Troubleshooting

### Email Not Sending

1. **Check connection string**: Ensure it's correctly copied from Azure Portal
2. **Verify domain**: Make sure domain is verified and linked
3. **Check sender address**: Must match your configured domain
4. **Rate limits**: Check if you've exceeded sending limits
5. **Logs**: Check application logs for error messages

### Emails Going to Spam

1. **SPF Record**: Add SPF record to your domain:
   ```
   v=spf1 include:spf.protection.outlook.com -all
   ```

2. **DKIM**: Configure DKIM signing in ACS Email settings

3. **Sender reputation**: Use consistent sender address

4. **Content**: Avoid spam trigger words

### Domain Verification Failing

1. **DNS propagation**: Wait 24-48 hours for DNS changes
2. **Correct records**: Double-check TXT and CNAME records
3. **Root domain**: Some registrars require @ or blank for root domain records

## Alternative: Microsoft Graph API

If you prefer to use Microsoft 365 mailboxes:

```python
import msal
import requests

# Configure Azure AD app with Mail.Send permission
app = msal.ConfidentialClientApplication(
    client_id="YOUR_CLIENT_ID",
    client_credential="YOUR_CLIENT_SECRET",
    authority=f"https://login.microsoftonline.com/{tenant_id}"
)

# Get token
token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

# Send email
requests.post(
    "https://graph.microsoft.com/v1.0/users/sender@yourdomain.com/sendMail",
    headers={"Authorization": f"Bearer {token['access_token']}"},
    json={
        "message": {
            "subject": "Test",
            "body": {"contentType": "HTML", "content": "<html>...</html>"},
            "toRecipients": [{"emailAddress": {"address": "recipient@example.com"}}]
        }
    }
)
```

## Production Recommendations

1. **Use custom domain** for professional appearance
2. **Monitor sending quotas** to avoid hitting limits
3. **Set up email alerts** for ACS service health
4. **Use managed identity** instead of connection string in production
5. **Implement retry logic** for transient failures
6. **Log all email activities** for audit trail

## Verification and Testing

### Verify Email Configuration

#### Check ACS Resource Status

```bash
# Verify ACS resources are properly configured
az communication show --name "acs-xcpeyeriwqbc4" --resource-group "rg-azdteamsmod2"

# Check email service status
az communication email show --name "ecs-xcpeyeriwqbc4" --resource-group "rg-azdteamsmod2"

# List configured domains
az communication email domain list --email-service-name "ecs-xcpeyeriwqbc4" --resource-group "rg-azdteamsmod2"
```

#### Verify Application Logs

```bash
# Check agent logs for email configuration
azd logs --service agent --tail 50 | grep -i "email\|notification"

# Look for successful email initialization
azd logs --service agent --tail 100 | grep "Email client initialized"

# Check for email sending attempts
azd logs --service agent --tail 100 | grep "Notification sent"
```

#### Test End-to-End Workflow

1. **Trigger a Test Moderation Event:**
   - Post a message in monitored Teams channel with test content
   - Or use the webhook test endpoint (if available)

2. **Monitor Agent Processing:**
   ```bash
   # Watch logs in real-time
   azd logs --service agent --follow
   ```

3. **Verify Email Delivery:**
   - Check recipient inbox (including spam folder)
   - Verify email content and formatting
   - Confirm violation details are accurate

## Production Configuration

### Configure Email Templates and Recipients

#### Customize Notification Recipients

**Multiple Recipients Configuration:**
```bash
# Configure multiple notification emails
azd env set NOTIFICATION_EMAIL "admin@company.com,security@company.com,hr@company.com"
```

**Role-Based Recipients:**
- **IT Administrators**: Technical issues and system alerts
- **HR Representatives**: Harassment and workplace conduct violations
- **Security Team**: PII detection and data privacy concerns
- **Team Moderators**: General content policy violations

#### Email Template Customization

The system supports customizable email templates in the UI dashboard:

1. **Access Template Configuration:**
   - Navigate to UI Dashboard → "Email Templates"
   - Customize templates for different violation types

2. **Template Variables Available:**
   - `{{violation_type}}` - Type of policy violation
   - `{{severity}}` - Violation severity level
   - `{{author}}` - Message author information
   - `{{channel}}` - Teams channel name
   - `{{message_content}}` - Original message content
   - `{{timestamp}}` - When violation occurred
   - `{{action_taken}}` - Action performed by system

### Security Best Practices

1. **Connection String Security:**
   ```bash
   # Store connection string in Azure Key Vault (recommended for production)
   az keyvault secret set \
     --vault-name "kv-teams-mod" \
     --name "email-connection-string" \
     --value "endpoint=https://...;accesskey=..."
   ```

2. **Sender Authentication:**
   - Configure SPF records: `v=spf1 include:spf.azurecomm.net ~all`
   - Set up DKIM signing for better deliverability
   - Configure DMARC policy for domain protection

3. **Email Rate Limiting:**
   - Monitor sending rates to stay within ACS limits
   - Implement email queuing for high-volume scenarios
   - Set up alerts for rate limit approaches

### Monitoring and Alerting

1. **ACS Metrics Monitoring:**
   ```bash
   # Create metric alerts for email delivery failures
   az monitor metrics alert create \
     --name "ACS-Email-Failures" \
     --resource-group "rg-azdteamsmod2" \
     --scopes "/subscriptions/{subscription-id}/resourceGroups/rg-azdteamsmod2/providers/Microsoft.Communication/CommunicationServices/acs-xcpeyeriwqbc4" \
     --condition "count 'DeliveryFailures' > 5" \
     --description "Alert when email delivery failures exceed threshold"
   ```

2. **Application-Level Monitoring:**
   - Set up Application Insights alerts for email sending errors
   - Monitor email delivery success rates
   - Track response times for email sending operations

## Cost Optimization

### Understand ACS Pricing

**Email Pricing Tiers:**
- **Free Tier**: 100 emails/month (development/testing)
- **Standard Tier**: $0.00025 per email (production)

**Cost Optimization Strategies:**
1. **Batch Notifications**: Group multiple violations into single email
2. **Severity-Based Filtering**: Only send emails for high/medium severity violations
3. **Time-Based Batching**: Send daily/hourly summaries instead of individual alerts
4. **Recipient Optimization**: Avoid duplicate emails to same recipients

### Monitor Usage and Costs

```bash
# Check ACS usage metrics
az monitor metrics list \
  --resource "/subscriptions/{subscription-id}/resourceGroups/rg-azdteamsmod2/providers/Microsoft.Communication/CommunicationServices/acs-xcpeyeriwqbc4" \
  --metric "EmailsSent" \
  --start-time 2026-01-01 \
  --end-time 2026-01-12
```

## Cost Estimation

For a team with 50 users and moderate activity:
- ~10 violations/day = 300 emails/month
- Cost: 300 × $0.00025 = **$0.075/month**

Very cost-effective for compliance and monitoring!
