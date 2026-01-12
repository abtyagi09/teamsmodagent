# 🚀 Getting Started with Teams Moderation

## Welcome to Your AI-Powered Teams Moderation System!

This system helps Russell Cellular automatically moderate Microsoft Teams content at scale using Azure AI.

---

## 📋 Quick Reference

### What You Have

✅ **Complete multi-agent AI system** built with Microsoft Agent Framework  
✅ **Azure AI Foundry integration** for intelligent content analysis  
✅ **Teams monitoring** via Microsoft Graph API  
✅ **Automated violation handling** with delete/flag/notify actions  
✅ **Production-ready deployment** with Docker and Azure guides  

### File Structure

```
teamschannelmod/
├── 📖 START_HERE.md           ← You are here!
├── 📖 README.md               ← Main documentation
├── 📖 QUICKSTART.md           ← 10-min setup guide
├── 📖 PROJECT_SUMMARY.md      ← What was built
├── 📖 ARCHITECTURE.md         ← Technical design
│
├── 📁 src/                    ← Application code
│   ├── main.py                ← Run this to start
│   ├── agents/                ← AI agents
│   ├── orchestrator/          ← Workflow
│   ├── integrations/          ← Teams API
│   └── utils/                 ← Helpers
│
├── 📁 ui/                     ← Configuration UI
│   ├── app.py                 ← Streamlit web app
│   ├── README.md              ← UI documentation
│   └── QUICKSTART.md          ← UI quick start
│
├── 📁 config/                 ← Settings
│   ├── channels.json          ← Which channels to monitor
│   └── policies.json          ← Moderation rules
│
├── 📁 deployment/             ← Production guides
│   ├── SETUP_GUIDE.md         ← Azure setup
│   └── DEPLOYMENT.md          ← Deploy to Azure
│
├── 📁 tests/                  ← Test suite
└── 📁 scripts/                ← Setup tools
    └── verify_setup.py        ← Check configuration
```

---

## 🎯 Your Next Steps

### Step 1: Review What Was Built (5 min)

Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) to understand the complete system.

**Key highlights:**
- Multi-agent architecture with Moderation + Notification agents
- Azure AI Foundry for LLM hosting (GPT-4o/GPT-4.1)
- Azure AI Content Safety for baseline detection
- Microsoft Graph API for Teams integration

### Step 2: Setup Azure Resources (30-60 min)

Follow [deployment/SETUP_GUIDE.md](deployment/SETUP_GUIDE.md) to create:
- ✅ Microsoft Foundry project with deployed model
- ✅ Azure AI Content Safety service
- ✅ Microsoft Entra ID app registration with Teams permissions
- ✅ Azure Key Vault (optional but recommended)

### Step 3: Configure Locally (10 min)

Follow [QUICKSTART.md](QUICKSTART.md) to:
- ✅ Install Python dependencies
- ✅ Configure environment variables
- ✅ Set up channel and policy configurations
- ✅ Test in dry-run mode

### Step 4: Deploy to Production (30 min)

Follow [deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md) to:
- ✅ Build Docker container
- ✅ Deploy to Azure Container Apps
- ✅ Configure monitoring and alerts

---

## ⚡ Quick Commands

### Launch Configuration UI

```powershell
streamlit run ui/app.py
```

Configure channels, policies, and test connections through the web interface.

### Verify Setup

```bash
python scripts/verify_setup.py
```

### Run in Test Mode (Dry Run)

```bash
python src/main.py --dry-run
```

### Monitor Specific Channel

```bash
python src/main.py --dry-run --channel general
```

### Run Tests

```bash
pytest tests/ -v
```

### Deploy to Azure

```bash
docker build -t teams-moderator:latest .
az containerapp create --name teams-moderator ...
```

---

## 📚 Documentation Guide

| Document | When to Read | Time |
|----------|-------------|------|
| **START_HERE.md** (this file) | First | 5 min |
| **PROJECT_SUMMARY.md** | Overview of what was built | 10 min |
| **QUICKSTART.md** | Setting up locally | 10 min |
| **deployment/SETUP_GUIDE.md** | Creating Azure resources | 30 min |
| **deployment/DEPLOYMENT.md** | Deploying to production | 30 min |
| **ARCHITECTURE.md** | Understanding the design | 15 min |
| **README.md** | Complete reference | 20 min |

---

## 🔧 Key Configuration Files

### `.env` - Environment Variables

```bash
# Microsoft Foundry
FOUNDRY_PROJECT_ENDPOINT=https://your-project.api.azureml.ms
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o

# Content Safety
CONTENT_SAFETY_ENDPOINT=https://your-safety.cognitiveservices.azure.com
CONTENT_SAFETY_KEY=your-key

# Teams
TEAMS_TENANT_ID=your-tenant-id
TEAMS_CLIENT_ID=your-client-id
TEAMS_CLIENT_SECRET=your-secret
TEAMS_TEAM_ID=your-team-id
```

### `config/channels.json` - Which Channels to Monitor

```json
{
  "monitored_channels": ["general", "frontline-workforce"],
  "excluded_channels": ["hr-private"]
}
```

### `config/policies.json` - Moderation Rules

```json
{
  "text_policies": {
    "hate_speech": {
      "enabled": true,
      "action": "delete",
      "notify": true
    }
  }
}
```

---

## 🎓 Understanding the System

### How It Works

1. **Monitor** - Polls Teams channels every 60 seconds for new messages
2. **Analyze** - Each message goes through:
   - Azure Content Safety (baseline detection)
   - AI Agent (contextual analysis)
   - Policy engine (action decision)
3. **Act** - Based on policies:
   - Delete violating messages
   - Flag for review
   - Send notifications to HR
4. **Log** - All actions recorded for audit

### Multi-Agent Architecture

```
Message → Moderation Agent → Decision → Notification Agent
              ↓
      (Content Safety + GPT-4o)
```

**Moderation Agent**: Analyzes content for violations  
**Notification Agent**: Composes and sends alerts  
**Orchestrator**: Coordinates the workflow  

---

## ⚠️ Important Notes

### Before Production

- [ ] Test thoroughly in dry-run mode
- [ ] Review and tune policies for your organization
- [ ] Set up admin notification channels
- [ ] Configure Azure Key Vault for secrets
- [ ] Enable monitoring and alerts

### Costs

**Estimated monthly Azure costs:** $165-320

Breakdown:
- Microsoft Foundry (GPT-4o): $110-220
- Azure Content Safety: $15-30
- Container Apps: $30-50
- Monitoring: $10-20

**Cost optimization:**
- Use `gpt-4.1-mini` instead of `gpt-4o` (80% cheaper)
- Increase polling interval
- Use consumption-based Container Apps

### Security

✅ Use Managed Identity in production (no keys in code)  
✅ Store secrets in Azure Key Vault  
✅ Enable VNet integration and Private Endpoints  
✅ Review logs regularly for audit compliance  

---

## 🆘 Getting Help

### Common Issues

**"Can't import agent_framework"**
```bash
pip install agent-framework-azure-ai --pre
```

**"Authentication failed"**
- Verify .env credentials
- Check app permissions granted admin consent
- Try `az login` for Azure authentication

**"Channel not found"**
- Verify TEAMS_TEAM_ID is correct
- Check channel names match exactly (case-sensitive)

### Support Resources

- 📖 Documentation: See all markdown files in project
- 🔧 Configuration: See `config/*.example.json`
- 🧪 Testing: See `tests/` directory
- 📧 IT Support: it-support@russellcellular.com

---

## ✅ Checklist for Success

### Pre-Launch Checklist

- [ ] Read PROJECT_SUMMARY.md
- [ ] Create all Azure resources (SETUP_GUIDE.md)
- [ ] Configure .env file
- [ ] Configure channels.json and policies.json
- [ ] Run verify_setup.py successfully
- [ ] Test in dry-run mode for 24 hours
- [ ] Review and approve first batch of detections
- [ ] Set up admin notifications
- [ ] Deploy to Azure Container Apps
- [ ] Enable monitoring and alerts

### Post-Launch Checklist

- [ ] Monitor logs daily for first week
- [ ] Review false positives
- [ ] Tune policy thresholds
- [ ] Gather HR feedback
- [ ] Document any issues
- [ ] Plan for image moderation (Phase 2)

---

## 🚀 Ready to Start?

### Recommended Path

1. **Read** → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) (10 min)
2. **Setup** → [deployment/SETUP_GUIDE.md](deployment/SETUP_GUIDE.md) (60 min)
3. **Test** → [QUICKSTART.md](QUICKSTART.md) (10 min)
4. **Deploy** → [deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md) (30 min)

### Or Jump Right In

```bash
# Quick start for testing
cd c:\agents\teamschannelmod
python -m venv venv
venv\Scripts\activate
pip install agent-framework-azure-ai --pre
pip install -r requirements.txt

# Copy and edit configuration
copy .env.example .env
copy config\channels.example.json config\channels.json
copy config\policies.example.json config\policies.json

# Verify setup
python scripts/verify_setup.py

# Run in test mode
python src/main.py --dry-run
```

---

## 🎉 You're All Set!

This system is production-ready and built entirely with Azure services:
- ✅ Microsoft Agent Framework
- ✅ Microsoft Foundry (Azure AI)
- ✅ Azure AI Content Safety
- ✅ Microsoft Graph API

**Questions?** See the documentation or contact IT support.

**Ready to scale Teams moderation at Russell Cellular!** 🚀

---

Built with ❤️ using Microsoft Agent Framework & Azure AI Foundry
