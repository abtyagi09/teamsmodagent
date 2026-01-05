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

### 7. Test Email Sending

```python
# Test script
from azure.communication.email import EmailClient

connection_string = "YOUR_CONNECTION_STRING"
client = EmailClient.from_connection_string(connection_string)

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

## Cost Estimation

For a team with 50 users and moderate activity:
- ~10 violations/day = 300 emails/month
- Cost: 300 × $0.00025 = **$0.075/month**

Very cost-effective for compliance and monitoring!
