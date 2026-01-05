# Teams Moderation Configuration UI - Quick Start

## Launch the UI

From the project root directory:

```powershell
streamlit run ui/app.py
```

The application opens at `http://localhost:8501`.

## Configuration Steps

### 1. Test Connection (30 seconds)

- Click "🔍 Test Connection" in the sidebar
- Click "Run Connection Tests"
- Verify all tests pass ✅

### 2. Configure Channels (2 minutes)

- Go to "📺 Channel Settings"
- Add channels to monitor:
  - Type channel name (e.g., "general")
  - Click "Add Monitored Channel"
- Add any exclusions:
  - Type channel name (e.g., "hr-private")
  - Click "Add Excluded Channel"
- Configure monitoring settings:
  - Enable real-time monitoring
  - Set batch interval if needed
- Click "Save Monitoring Settings"

### 3. Set Moderation Policies (3 minutes)

- Go to "📋 Moderation Policies"
- For each policy (hate_speech, profanity, etc.):
  - Expand the policy section
  - Toggle "Enabled"
  - Set threshold: `low`, `medium`, or `high`
  - Choose action: `delete`, `flag`, `archive`
  - Enable/disable notifications
  - Click "Save"

**Recommended Starting Configuration:**

| Policy | Enabled | Threshold | Action | Notify |
|--------|---------|-----------|--------|--------|
| Hate Speech | ✅ | Medium | Delete | ✅ |
| Profanity | ✅ | High | Flag | ❌ |
| Violence | ✅ | Medium | Delete | ✅ |
| Self Harm | ✅ | Low | Delete | ✅ |
| Sexual Content | ✅ | Medium | Delete | ✅ |
| PII Leak | ✅ | Low | Flag | ✅ |

### 4. Review System Settings

- Go to "⚙️ System Settings"
- Verify all configuration is correct
- Note any missing settings

### 5. Start Monitoring

Close the UI and run:

```powershell
# Test first with dry-run
python src/main.py --dry-run

# If successful, start production monitoring
python src/main.py
```

## Common Tasks

### Add a New Channel

1. Open UI: `streamlit run ui/app.py`
2. Go to "Channel Settings"
3. Enter channel name
4. Click "Add Monitored Channel"

### Disable a Policy Temporarily

1. Open UI
2. Go to "Moderation Policies"
3. Expand the policy
4. Uncheck "Enabled"
5. Click "Save"

### Adjust Sensitivity

To reduce false positives:
1. Increase threshold from `low` → `medium` → `high`
2. Or change action from `delete` → `flag`

To increase sensitivity:
1. Decrease threshold from `high` → `medium` → `low`

### View Current Configuration

1. Open UI
2. Each tab has "View Full Configuration" expander
3. Or check JSON files in `config/` directory

## Troubleshooting

### UI Won't Start

```powershell
# Install Streamlit
pip install streamlit

# Verify
streamlit --version
```

### Changes Not Saving

- Check file permissions on `config/` directory
- Ensure you're running from project root
- Check browser console for errors

### Connection Tests Fail

```powershell
# Run detailed diagnostics
python scripts/verify_setup.py
```

### Need to Reset Configuration

```powershell
# Restore from examples
copy config\channels.example.json config\channels.json
copy config\policies.example.json config\policies.json
```

## Configuration Files

The UI modifies:
- `config/channels.json` - Channel monitoring settings
- `config/policies.json` - Moderation policy rules

To view or edit manually:

```powershell
notepad config\channels.json
notepad config\policies.json
```

## Next Steps

After configuration:

1. **Test**: `python src/main.py --dry-run`
2. **Monitor specific channels**: `python src/main.py --channel general`
3. **Production**: `python src/main.py`
4. **Review logs**: Check `logs/` directory

## Documentation

- [Full UI Guide](README.md) - Complete feature documentation
- [Main Project Guide](../README.md) - System overview
- [Setup Guide](../deployment/SETUP_GUIDE.md) - Azure resources
- [Architecture](../ARCHITECTURE.md) - System design
