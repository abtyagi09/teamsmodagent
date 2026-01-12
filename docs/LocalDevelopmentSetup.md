# Local Development Setup Guide

This guide provides comprehensive instructions for setting up the Teams Channel Moderation solution for local development.

## Important Setup Notes

### Multi-Service Architecture

This solution consists of multiple services that work together:
- **Agent Service**: Monitors Teams channels and performs content moderation
- **UI Service**: Streamlit web dashboard for configuration and monitoring
- **Infrastructure**: Azure resources (AI Foundry, Content Safety, Communication Services)

### Configuration Files

This project uses a `.env` file in the root directory with configuration requirements:
- **Main**: `.env` - Contains all Azure service connections and Teams configuration

---

## Step 1: Prerequisites - Install Required Tools

### Windows Development

**Required Software:**
1. **[Python 3.9+](https://www.python.org/downloads/)** - Programming language runtime
2. **[Git](https://git-scm.com/downloads)** - Version control system  
3. **[VS Code](https://code.visualstudio.com/)** (recommended) - Code editor with Python support
4. **[Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)** - Azure management tool
5. **[Azure Developer CLI (azd)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)** - Deployment tool

### Clone the Repository

```bash
git clone <your-repository-url>
cd teamschannelmod
```

---

## Step 2: Development Tools Setup

### Visual Studio Code (Recommended)

**Required Extensions:**
- Python Extension Pack
- Azure Tools Extension Pack
- Docker Extension (if using containers)

**Settings Configuration:**
Create a `.vscode/settings.json` file:
```json
{
    "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true
}
```

---

## Step 3: Azure Authentication Setup

### Authenticate with Azure

```bash
az login
azd auth login
```

### Required Azure RBAC Permissions

Your Azure account needs the following role assignments on the deployed resources:

#### AI Foundry Access
```bash
# Get your user principal ID
az ad signed-in-user show --query id -o tsv

# Assign AI Foundry roles
az role assignment create \
    --assignee <your-user-principal-id> \
    --role "Azure AI Developer" \
    --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>
```

#### Content Safety Access
```bash
az role assignment create \
    --assignee <your-user-principal-id> \
    --role "Cognitive Services User" \
    --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>
```

---

## Step 4: Backend Setup & Run Instructions

### 4.1 Navigate to Project Directory

```bash
# Ensure you're in the repository root
pwd  # Should show: .../teamschannelmod
```

### 4.2 Configure Environment Variables

**Step 1: Create the `.env` file**

```bash
# Create .env file
touch .env  # Linux/macOS
# or
New-Item .env  # Windows PowerShell
```

**Step 2: Copy the template**

1. Copy contents from `.env.example`
2. Update the `.env` file with your Azure resource values

**Step 3: Get Azure values and update `.env`**

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to your **Resource Group**
3. Copy values from your deployed resources:
   - AI Foundry project endpoint
   - Content Safety endpoint and key
   - Communication Services connection string
   - Teams app registration details

**Required Environment Variables:**
```env
# Microsoft Foundry Configuration
FOUNDRY_PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com/
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o-mini

# Azure Content Safety
CONTENT_SAFETY_ENDPOINT=https://your-content-safety.cognitiveservices.azure.com/
CONTENT_SAFETY_KEY=your-content-safety-key

# Microsoft Teams Integration
TEAMS_TENANT_ID=your-tenant-id
TEAMS_CLIENT_ID=your-client-id
TEAMS_CLIENT_SECRET=your-client-secret
TEAMS_TEAM_ID=your-team-id

# Email Notifications (Azure Communication Services)
EMAIL_CONNECTION_STRING=endpoint=https://your-acs.communication.azure.com/;accesskey=your-key
EMAIL_SENDER=DoNotReply@your-domain.azurecomm.net
NOTIFICATION_EMAIL=admin@yourcompany.com

# Configuration
CONFIG_CONNECTION_STRING=Endpoint=https://your-appconfig.azconfig.io;Id=your-id;Secret=your-secret
```

### 4.3 Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

### 4.4 Run the Agent

```bash
# Run the main agent
python -m src.main
```

The agent will start monitoring Teams channels and processing messages according to configured policies.

---

## Step 5: UI Setup & Run Instructions

### 5.1 Navigate to UI Directory

```bash
cd ui
```

### 5.2 Install UI Dependencies

```bash
# UI uses the same virtual environment and requirements
# Dependencies should already be installed from Step 4.3
```

### 5.3 Start UI Server

```bash
# From the ui directory
streamlit run app.py
```

The UI will start at: `http://localhost:8501`

**Or from repository root:**
```bash
streamlit run ui/app.py
```

---

## Step 6: Configure Through UI

Once both services are running:

1. **Open UI Dashboard**: Navigate to `http://localhost:8501`
2. **Configure Policies**: Set up moderation rules and thresholds
3. **Configure Channels**: Select Teams channels to monitor
4. **Test Configuration**: Use the test functions to verify setup
5. **Save Configuration**: Click "Save" to store settings

---

## Step 7: Verify All Services Are Running

### Check Agent Status
```bash
# In the terminal running the agent, you should see:
# "✅ Agent initialized successfully"
# "🔍 Polling Teams channels..."
# "📝 Processing message: [message-id]"
```

### Check UI Status
```bash
# In the terminal running Streamlit, you should see:
# "You can now view your Streamlit app in your browser."
# "Local URL: http://localhost:8501"
```

### Test Integration
1. Open UI at `http://localhost:8501`
2. Navigate to "Test" section
3. Click "Test Email Notification"
4. Verify email is received

---

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)

**Authentication Errors:**
- Verify Azure CLI login: `az account show`
- Check role assignments for your user
- Ensure correct resource group and subscription

**Environment Variable Issues:**
- Verify `.env` file exists and has correct values
- Check for typos in environment variable names
- Ensure no spaces around `=` in environment variables

### Agent Not Processing Messages
1. Check Teams app registration permissions
2. Verify Team ID is correct
3. Check agent logs for error messages
4. Ensure policies are configured in UI

### UI Not Saving Configuration
1. Verify Azure App Configuration connection string
2. Check managed identity permissions
3. Review browser console for errors
4. Ensure "Save" button is clicked

---

## Step 8: Next Steps

Once all services are running:

1. **Configure Policies**: Set up appropriate content moderation rules
2. **Monitor Channels**: Watch the agent logs to see message processing
3. **Test Notifications**: Verify email alerts are working correctly
4. **Tune Settings**: Adjust policies based on detected content

## Related Documentation

- [Deployment Guide](DeploymentGuide.md) - Production deployment instructions
- [Configuration Guide](CONFIGURATION_ARCHITECTURE.md) - Detailed configuration options
- [Email Setup](EMAIL_SETUP.md) - Email notification configuration