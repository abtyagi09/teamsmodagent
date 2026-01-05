# Quick Start Guide

## Get Your Teams Moderation System Running in 10 Minutes

This guide gets you up and running quickly for local testing.

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Azure subscription access
- [ ] Microsoft Foundry project with deployed model
- [ ] Azure AI Content Safety resource created
- [ ] Teams admin permissions
- [ ] Microsoft Entra ID app registered with Graph API permissions

> **Don't have these yet?** See [SETUP_GUIDE.md](deployment/SETUP_GUIDE.md) for detailed setup instructions.

## Step 1: Clone and Setup (2 minutes)

```bash
cd c:\agents\teamschannelmod

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies (includes --pre flag for agent-framework)
pip install agent-framework-azure-ai --pre
pip install -r requirements.txt
```

## Step 2: Configure Environment (3 minutes)

### Option A: Use Configuration UI (Recommended)

```powershell
# Install Streamlit if needed
pip install streamlit

# Launch the configuration UI
streamlit run ui/app.py
```

In the web interface:
1. Click "Test Connection" to verify setup
2. Go to "Channel Settings" to add channels
3. Configure "Moderation Policies" as needed
4. Review "System Settings"

### Option B: Manual Configuration

Copy and edit the environment file:

```bash
copy .env.example .env
notepad .env
```

Fill in your values:

```bash
# Required: Microsoft Foundry
FOUNDRY_PROJECT_ENDPOINT=https://your-project.eastus.api.azureml.ms
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o

# Required: Content Safety
CONTENT_SAFETY_ENDPOINT=https://your-content-safety.cognitiveservices.azure.com
CONTENT_SAFETY_KEY=your-key-here

# Required: Teams
TEAMS_TENANT_ID=your-tenant-id
TEAMS_CLIENT_ID=your-client-id
TEAMS_CLIENT_SECRET=your-client-secret
TEAMS_TEAM_ID=your-team-id

# Optional: Notifications
NOTIFICATION_EMAIL=hr@russellcellular.com
NOTIFICATION_WEBHOOK=https://outlook.office.com/webhook/...

# Settings
LOG_LEVEL=INFO
MODERATION_MODE=monitor
POLLING_INTERVAL=60
```

## Step 3: Configure Channels (2 minutes)

Copy example config and edit:

```bash
copy config\channels.example.json config\channels.json
copy config\policies.example.json config\policies.json

notepad config\channels.json
```

Edit to match your Teams channels:

```json
{
  "monitored_channels": [
    "general",
    "frontline-workforce"
  ],
  "excluded_channels": [
    "hr-private"
  ]
}
```

## Step 4: Test Configuration (1 minute)

Verify your setup:

```bash
python -c "from src.utils.config_loader import get_settings; print('✅ Configuration loaded successfully!')"
```

## Step 5: Run in Dry-Run Mode (2 minutes)

Test without actually deleting anything:

```bash
python src/main.py --dry-run --log-level DEBUG
```

You should see:

```
🚀 Starting Teams moderation workflow
📺 Monitoring channels: general, frontline-workforce
🔄 Polling interval: 60 seconds
🧪 DRY RUN MODE - No messages will be deleted
```

## Step 6: Monitor a Specific Channel

Test on just one channel first:

```bash
python src/main.py --dry-run --channel general
```

## What Happens Next?

The system will:
1. 🔍 Poll Teams channels every 60 seconds
2. 📨 Retrieve new messages
3. 🤖 Analyze each message using AI agents
4. 📊 Log results (in dry-run mode)
5. 🔔 Send notifications for violations (if configured)

## Troubleshooting Common Issues

### "ModuleNotFoundError: No module named 'agent_framework'"

```bash
# Make sure to use --pre flag
pip install agent-framework-azure-ai --pre
```

### "Authentication failed"

- Verify your `.env` credentials
- Check that app permissions were granted admin consent
- Try: `az login` if using Managed Identity

### "Team or channel not found"

- Verify TEAMS_TEAM_ID is correct
- Check channel names match exactly (case-sensitive)
- Ensure app has `Team.ReadBasic.All` permission

### "Content Safety 403 error"

- Verify CONTENT_SAFETY_KEY is correct
- Check that the key isn't expired
- Ensure endpoint URL is correct

## Next Steps

### Ready for Production?

1. **Test thoroughly** in dry-run mode
2. **Tune policies** in `config/policies.json`
3. **Enable enforcement mode**: Change `MODERATION_MODE=enforce` in `.env`
4. **Deploy to Azure**: Follow [DEPLOYMENT.md](deployment/DEPLOYMENT.md)

### Review Policy Settings

Edit `config/policies.json` to customize:

```json
{
  "text_policies": {
    "hate_speech": {
      "enabled": true,
      "threshold": "medium",
      "action": "delete",    // or "flag" or "archive"
      "notify": true
    },
    "profanity": {
      "enabled": true,
      "threshold": "high",
      "action": "flag",      // Less severe action
      "notify": false
    }
  }
}
```

### Enable Notifications

Set up Teams webhook for admin alerts:

1. Go to your admin Teams channel
2. Click ⚙️ → Connectors → Incoming Webhook
3. Name it "Moderation Alerts"
4. Copy webhook URL
5. Add to `.env`: `NOTIFICATION_WEBHOOK=<url>`

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest tests/ -v
```

## Monitoring in Production

View logs:

```bash
# Real-time logs
tail -f logs/moderation.log

# Search for violations
grep "violation" logs/moderation.log

# Count actions taken
grep "action_taken" logs/moderation.log | wc -l
```

## Getting Help

- 📖 Full documentation: [README.md](README.md)
- ⚙️ Azure setup: [SETUP_GUIDE.md](deployment/SETUP_GUIDE.md)
- 🚀 Deployment: [DEPLOYMENT.md](deployment/DEPLOYMENT.md)
- 📧 Support: it-support@russellcellular.com

## Architecture Reminder

```
Teams Channels → Monitor → Moderation Agent → Decision → Action
                              ↓
                        Notification Agent → Alerts
```

**Built with Microsoft Agent Framework & Azure AI Foundry** ✨

---

🎉 **Congratulations!** You now have an AI-powered Teams moderation system running!
