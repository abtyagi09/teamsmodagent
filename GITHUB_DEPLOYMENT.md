# GitHub Deployment Instructions

Your Teams moderation system has been initialized as a Git repository and is ready to push to GitHub.

## Quick Start - Push to GitHub

### Option 1: Create New Repository on GitHub (Recommended)

1. **Go to GitHub** → https://github.com/new
2. **Repository Name**: `teams-moderation-system` (or your preferred name)
3. **Description**: "AI-driven content moderation system for Microsoft Teams"
4. **Visibility**: Choose `Private` (for company use)
5. **Click "Create repository"**

### Option 2: Link to Existing Repository

If you already have a repo created, skip to step 5 below.

### Step 1: Copy the Remote URL

After creating the repo, GitHub will show you the HTTPS or SSH URL:
```
https://github.com/YOUR_USERNAME/teams-moderation-system.git
```

### Step 2: Add Remote and Push

```powershell
cd c:\agents\teamschannelmod

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/teams-moderation-system.git

# Rename branch if needed (GitHub uses 'main' by default)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 3: Verify on GitHub

Visit your repository URL to see all files uploaded:
```
https://github.com/YOUR_USERNAME/teams-moderation-system
```

## If Using SSH (Recommended for Automation)

1. **Generate SSH key** (if you don't have one):
```powershell
ssh-keygen -t ed25519 -C "your-email@russellcellular.com"
```

2. **Add to GitHub**:
   - Go to https://github.com/settings/keys
   - Click "New SSH key"
   - Paste the public key from `~/.ssh/id_ed25519.pub`

3. **Add remote with SSH**:
```powershell
git remote add origin git@github.com:YOUR_USERNAME/teams-moderation-system.git
git push -u origin main
```

## Current Repository Status

✅ **Initialized**: Git repository created
✅ **Committed**: 35 files, 6450 lines of code
✅ **Tracked**: All project files
❌ **Remote**: Not yet connected to GitHub

### What's in the Repository:

```
teams-moderation-system/
├── src/                          # Main application code
│   ├── agents/                   # AI agents (Moderation, Notification)
│   ├── orchestrator/             # Multi-agent workflow
│   ├── integrations/             # Teams Graph API client
│   └── utils/                    # Configuration and logging
├── ui/                           # Streamlit configuration interface
├── config/                       # Configuration files
├── tests/                        # Test suite
├── deployment/                   # Azure deployment guides
├── scripts/                      # Setup utilities
├── Dockerfile                    # Container image
├── requirements.txt              # Python dependencies
├── README.md                     # Main documentation
├── QUICKSTART.md                 # Quick start guide
├── TESTING_GUIDE.md              # Comprehensive testing guide
├── ARCHITECTURE.md               # Technical architecture
└── PROJECT_SUMMARY.md            # Project overview
```

## Git Commands Reference

```powershell
# Check current remote
git remote -v

# View commit history
git log --oneline

# View branches
git branch -a

# Create a new branch for features
git checkout -b feature/new-feature
git add .
git commit -m "Description"
git push origin feature/new-feature
```

## .env Security Note

⚠️ **IMPORTANT**: The `.env` file is in `.gitignore` and will NOT be pushed to GitHub.

Users pulling the repo will copy `.env.example` to `.env` and fill in their own credentials:

```powershell
copy .env.example .env
notepad .env
```

## Collaboration Setup

### For Team Members

After pushing to GitHub, team members can:

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/teams-moderation-system.git
cd teams-moderation-system

# Setup local environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
notepad .env  # Add your Azure credentials

# Run tests
python test_e2e.py

# Launch configuration UI
streamlit run ui/app.py
```

## CI/CD Integration (Optional)

To automate testing on every push:

1. Create `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

2. Push the workflow:
```powershell
git add .github/workflows/test.yml
git commit -m "Add CI/CD workflow"
git push
```

## Protecting the Repository

Recommended GitHub settings:

1. **Settings** → **Branches** → Add rule for `main`:
   - ✅ Require pull request reviews (2 reviews)
   - ✅ Require status checks to pass
   - ✅ Dismiss stale reviews
   - ✅ Require branches to be up to date

2. **Settings** → **Secrets and variables**:
   - Add Azure credentials as GitHub Secrets for CI/CD

## Next Steps After Pushing

1. **Share the link** with your team:
   ```
   https://github.com/YOUR_USERNAME/teams-moderation-system
   ```

2. **Update documentation** with your GitHub URL

3. **Setup Azure DevOps** for automated deployment (optional):
   - Create pipeline in Azure DevOps
   - Connect to GitHub repo
   - Deploy to Azure Container Apps

4. **Monitor the repository**:
   - Setup branch protection rules
   - Configure status checks
   - Enable security scanning

## Troubleshooting

### "fatal: 'origin' does not appear to be a 'git' repository"

Solution:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/teams-moderation-system.git
git push -u origin main
```

### "Permission denied (publickey)"

Solution: Setup SSH key properly (see SSH section above) or use HTTPS with personal access token:
```powershell
git remote set-url origin https://YOUR_USERNAME:PERSONAL_TOKEN@github.com/YOUR_USERNAME/teams-moderation-system.git
```

### "Everything up-to-date" but files not showing

Solution:
```powershell
git status  # Check what's staged
git push -f origin main  # Force push (use carefully!)
```

## Support

For GitHub help:
- GitHub Docs: https://docs.github.com
- Teams moderation README: See [README.md](README.md)
- Architecture details: See [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Your repository is ready for GitHub! 🚀**

Replace `YOUR_USERNAME` with your actual GitHub username and run the commands above to push your Teams moderation system to GitHub.
