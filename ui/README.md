# Teams Moderation Configuration UI

Web-based user interface for configuring the Teams moderation system.

## Overview

This Streamlit application provides an intuitive interface for:

- **Channel Management**: Configure which Teams channels to monitor or exclude
- **Policy Configuration**: Enable/disable moderation policies and set thresholds
- **System Settings**: View current Azure and Teams configuration
- **Connection Testing**: Verify setup and connectivity

## Installation

1. Install Streamlit (if not already installed):

```powershell
pip install streamlit
```

2. Ensure you're in the project root directory with proper `.env` configuration.

## Running the UI

From the project root directory:

```powershell
streamlit run ui/app.py
```

The application will open in your default browser at `http://localhost:8501`.

## Features

### 📺 Channel Settings

- **Monitored Channels**: Add/remove channels where moderation is active
- **Excluded Channels**: Specify channels to skip during monitoring
- **Monitoring Settings**: Configure real-time vs. batch scanning options

#### Adding Channels

1. Navigate to "Channel Settings"
2. Enter the channel name (e.g., "general", "random")
3. Click "Add Monitored Channel" or "Add Excluded Channel"
4. Changes are saved immediately to `config/channels.json`

### 📋 Moderation Policies

Configure individual content policies:

- **Hate Speech**: Discrimination, harassment, hate speech
- **Profanity**: Offensive language
- **Violence**: Violent or threatening content
- **Self Harm**: Self-harm related content
- **Sexual Content**: Sexually explicit material
- **PII Leak**: Personally identifiable information

For each policy, you can:

- ✅ Enable/disable the policy
- 🎯 Set threshold: `low`, `medium`, or `high`
- ⚡ Choose action: `delete`, `flag`, `archive`, or `allow`
- 📧 Toggle notifications to HR/admins

#### Threshold Levels

- **Low** (0-30%): Most sensitive, catches more potential violations
- **Medium** (31-70%): Balanced detection
- **High** (71-100%): Only high-confidence violations

#### Actions

- **Delete**: Immediately remove the message
- **Flag**: Mark for review without deletion
- **Archive**: Move to archive channel for investigation
- **Allow**: Log but take no action

### ⚙️ System Settings

View current configuration from `.env`:

- Microsoft Foundry endpoint and model deployment
- Azure Content Safety service details
- Teams tenant, client, and team IDs
- Application settings (log level, polling interval)
- Notification settings (email, webhooks)

**Note**: Settings are read-only in the UI. To modify, edit `.env` and restart the application.

### 🔍 Test Connection

Run comprehensive connection tests:

1. **Environment Configuration**: Verify `.env` loads correctly
2. **Configuration Files**: Check channels.json and policies.json
3. **Python Dependencies**: Validate required modules are installed
4. **File System Access**: Ensure write permissions for config/logs

Manual tests available for:
- Microsoft Foundry connectivity
- Teams Graph API access

## Configuration Files

The UI modifies two JSON configuration files:

### config/channels.json

```json
{
  "monitored_channels": ["general", "team-chat"],
  "excluded_channels": ["hr-private", "executives"],
  "monitoring_settings": {
    "enable_real_time": true,
    "enable_batch_scan": false,
    "batch_interval_minutes": 60
  }
}
```

### config/policies.json

```json
{
  "text_policies": {
    "hate_speech": {
      "enabled": true,
      "threshold": "medium",
      "action": "delete",
      "notify": true,
      "description": "Detects hate speech, discrimination, or harassment"
    },
    ...
  }
}
```

## Usage Workflow

### Initial Setup

1. **Start the UI**: `streamlit run ui/app.py`
2. **Test Connection**: Click "Test Connection" to verify setup
3. **Configure Channels**: Add Teams channels to monitor
4. **Set Policies**: Enable and configure moderation rules
5. **Test**: Run main app with `--dry-run` to test without deleting

### Ongoing Management

1. **Add/Remove Channels**: As your Teams environment evolves
2. **Adjust Policies**: Fine-tune thresholds based on false positive rates
3. **Review Settings**: Regularly check system configuration
4. **Monitor Logs**: Use logs to identify policy effectiveness

## Troubleshooting

### UI Won't Start

```powershell
# Install Streamlit
pip install streamlit

# Verify installation
streamlit --version
```

### Configuration Not Loading

- Ensure you're in the project root directory
- Check that `config/` directory exists
- Verify `.env` file is present (copy from `.env.example`)

### Changes Not Saving

- Check file permissions on `config/` directory
- Ensure `channels.json` and `policies.json` are writable
- Review browser console for errors

### Connection Tests Failing

Run the verification script:

```powershell
python scripts/verify_setup.py
```

This provides detailed diagnostics.

## Port Configuration

By default, Streamlit runs on port 8501. To change:

```powershell
streamlit run ui/app.py --server.port 8080
```

## Security Considerations

- **Local Use**: UI is designed for local configuration management
- **Production**: For production deployments, consider adding authentication
- **Credentials**: Sensitive values from `.env` are masked in the UI
- **Access Control**: Restrict access to the UI server

## Future Enhancements

Planned features:

- 🔍 **Channel Discovery**: Fetch actual channel list from Teams Graph API
- 📊 **Analytics Dashboard**: View moderation statistics and trends
- 👥 **User Management**: Configure admin/reviewer roles
- 🔔 **Live Notifications**: Real-time alerts for violations
- 📝 **Audit Log Viewer**: Browse moderation history
- 🎨 **Theme Customization**: Match your organization's branding

## Integration with Main Application

After configuring via the UI:

1. **Dry Run**: Test configuration without deleting
   ```powershell
   python src/main.py --dry-run
   ```

2. **Production**: Start monitoring
   ```powershell
   python src/main.py
   ```

3. **Specific Channels**: Monitor only certain channels
   ```powershell
   python src/main.py --channel general --channel team-chat
   ```

## Support

For issues or questions:

- Check `deployment/SETUP_GUIDE.md` for Azure setup
- Review `QUICKSTART.md` for getting started
- Run `python scripts/verify_setup.py` for diagnostics
- Check application logs in `logs/` directory

## Architecture

The UI is built with:

- **Streamlit**: Python web framework for data apps
- **JSON Configuration**: Direct manipulation of config files
- **Settings Integration**: Uses existing `config_loader.py` module
- **Responsive Design**: Works on desktop and tablet screens

## Development

To modify the UI:

1. Edit `ui/app.py`
2. Changes are hot-reloaded automatically
3. Use `st.rerun()` to refresh state after config changes
4. Follow Streamlit best practices for session state management
