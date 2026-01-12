# Teams Entra ID Setup Guide

This guide provides step-by-step instructions for configuring Microsoft Teams integration through Entra ID (formerly Azure Active Directory) for the Teams Channel Moderation solution.

## Prerequisites

- Azure subscription with appropriate permissions
- Microsoft 365 tenant with Teams enabled
- Global Administrator or Application Administrator role in Entra ID
- PowerShell (optional, for advanced Team ID discovery)

## Setup Process

### Step 1: Create Entra ID App Registration

1. **Access Entra ID Portal:**
   - Navigate to [Azure Portal](https://portal.azure.com)
   - Search for and select "Microsoft Entra ID" or "Azure Active Directory"
   - Select "App registrations" from the left navigation menu

2. **Create New Registration:**
   - Click "New registration"
   - Fill in the registration details:
     ```
     Name: Teams Channel Moderation Bot
     Supported account types: Accounts in this organizational directory only (Single tenant)
     Redirect URI: Leave empty (we'll configure this if needed later)
     ```
   - Click "Register"

3. **Capture Application Details:**
   After registration, note these values from the Overview page:
   - **Application (client) ID** → Use for `TEAMS_CLIENT_ID`
   - **Directory (tenant) ID** → Use for `TEAMS_TENANT_ID`

### Step 2: Configure API Permissions

1. **Navigate to API Permissions:**
   - In your app registration, select "API permissions" from the left menu
   - Click "Add a permission"

2. **Add Microsoft Graph Permissions:**
   - Select "Microsoft Graph"
   - Choose "Application permissions" (not Delegated permissions)
   - Add the following permissions:

   | Permission | Purpose |
   |------------|---------|
   | `Channel.ReadBasic.All` | Read basic properties of all channels |
   | `ChannelMessage.Read.All` | Read messages in all channels |
   | `Team.ReadBasic.All` | Read basic properties of all teams |
   | `TeamsAppInstallation.Read.All` | Read Teams app installations |
   | `User.Read.All` | Read user profile information |

3. **Grant Admin Consent:**
   - After adding all permissions, click "Grant admin consent for [Organization Name]"
   - Click "Yes" to confirm
   - Verify all permissions show "Granted for [Organization Name]"

### Step 3: Create Client Secret

1. **Access Certificates & Secrets:**
   - Select "Certificates & secrets" from the left menu
   - Click "New client secret"

2. **Configure Secret:**
   ```
   Description: Teams Moderation Bot Secret
   Expires: 24 months (recommended for production)
   ```

3. **Copy Secret Value:**
   - **CRITICAL:** Immediately copy the secret **Value** (not the Secret ID)
   - Store securely - this value cannot be retrieved again
   - Use this value for `TEAMS_CLIENT_SECRET`

### Step 4: Discover Team Information

#### Method 1: Using Teams Web Interface

1. **Get Team ID from URL:**
   - Open Microsoft Teams in web browser
   - Navigate to your target team
   - Click the "..." (more options) next to the team name
   - Select "Get link to team"
   - Copy the URL which looks like:
     ```
     https://teams.microsoft.com/l/team/19%3A[ENCODED-TEAM-ID]%40thread.tacv2/conversations?groupId=[GROUP-ID]
     ```
   - The Team ID is the decoded portion between `19%3A` and `%40thread.tacv2`

#### Method 2: Using PowerShell (Advanced)

```powershell
# Install Microsoft Teams PowerShell module (if not already installed)
Install-Module -Name MicrosoftTeams -Force -AllowClobber

# Connect to Microsoft Teams
Connect-MicrosoftTeams

# List all teams you have access to
Get-Team | Select-Object DisplayName, GroupId, Description

# Get specific team by name
$team = Get-Team -DisplayName "Your Team Name Here"
Write-Host "Team ID: $($team.GroupId)"

# List channels in the team
Get-TeamChannel -GroupId $team.GroupId | Select-Object DisplayName, Id, Description

# Disconnect when done
Disconnect-MicrosoftTeams
```

#### Method 3: Using Graph Explorer

1. Navigate to [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
2. Sign in with your Microsoft 365 account
3. Run the query: `GET https://graph.microsoft.com/v1.0/me/joinedTeams`
4. Find your team in the results and copy the `id` field

### Step 5: Configure Application

Update your application deployment with the collected values:

```bash
# Set environment variables
azd env set TEAMS_TENANT_ID "your-directory-tenant-id"
azd env set TEAMS_CLIENT_ID "your-application-client-id"
azd env set TEAMS_CLIENT_SECRET "your-client-secret-value"
azd env set TEAMS_TEAM_ID "your-team-id"

# Deploy the updated configuration
azd up
```

### Step 6: Verify Configuration

1. **Check Application Logs:**
   ```bash
   # View agent logs to verify Teams connection
   azd logs --service agent --follow
   
   # Look for successful Teams authentication messages
   azd logs --service agent --tail 50 | grep -i "teams\|auth"
   ```

2. **Test Through UI:**
   - Access the web UI dashboard
   - Navigate to Teams configuration section
   - Verify connection status
   - Test channel discovery functionality

## Security Best Practices

### App Registration Security

1. **Secret Management:**
   - Store secrets in Azure Key Vault in production
   - Rotate secrets every 12-24 months
   - Never store secrets in source code or configuration files
   - Use managed identities when possible

2. **Permission Management:**
   - Follow principle of least privilege
   - Regularly audit granted permissions
   - Remove unnecessary permissions
   - Document all permission changes

3. **Access Control:**
   - Limit app registration ownership to essential personnel
   - Use Azure AD Privileged Identity Management (PIM)
   - Enable multi-factor authentication for app owners
   - Conduct regular access reviews

### Monitoring and Auditing

1. **Enable Audit Logs:**
   - Monitor app registration changes
   - Track permission grants and modifications
   - Review sign-in logs for the application
   - Set up alerts for suspicious activity

2. **Regular Reviews:**
   - Quarterly permission reviews
   - Annual security assessment
   - Monitor Teams API usage patterns
   - Review detected content patterns

## Troubleshooting

### Common Issues

1. **"Forbidden" or 401 Authentication Errors:**
   - Verify client ID and secret are correct
   - Check that admin consent was granted
   - Ensure the correct tenant ID is configured

2. **"Insufficient Privileges" Errors:**
   - Verify all required permissions are granted
   - Check that admin consent is complete
   - Ensure permissions are Application-type, not Delegated

3. **Cannot Find Teams/Channels:**
   - Verify the Team ID is correct
   - Check that the app has access to the team
   - Ensure the user account used for setup is a member of the team

4. **Secret Expired Errors:**
   - Check secret expiration date in Entra ID
   - Generate new secret if expired
   - Update application configuration with new secret

### Validation Commands

```bash
# Test Graph API connectivity
curl -X GET \
  'https://graph.microsoft.com/v1.0/teams/{team-id}' \
  -H 'Authorization: Bearer {access-token}'

# Validate team access
curl -X GET \
  'https://graph.microsoft.com/v1.0/teams/{team-id}/channels' \
  -H 'Authorization: Bearer {access-token}'
```

## Support

For additional support:

1. **Microsoft Graph API Documentation:** https://docs.microsoft.com/en-us/graph/
2. **Teams App Development:** https://docs.microsoft.com/en-us/microsoftteams/
3. **Entra ID App Registration:** https://docs.microsoft.com/en-us/azure/active-directory/develop/

---

**Next:** Return to [Deployment Guide](DeploymentGuide.md) to continue with email notification setup.