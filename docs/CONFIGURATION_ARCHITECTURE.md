# Configuration Management Architecture

## Overview

The Teams Moderation system uses **Azure App Configuration** as a centralized configuration store with **dynamic refresh capabilities**. This allows the UI and agent containers to share configuration data, and the agent automatically picks up configuration changes without requiring restarts.

## Architecture

```
┌─────────────────┐
│   UI Container  │
│   (Streamlit)   │
└────────┬────────┘
         │ Write configs
         ▼
┌─────────────────────────┐
│ Azure App Configuration │
│  - channels.json        │  ← Automatically refreshed
│  - policies.json        │     every N seconds
└────────┬────────────────┘
         │ Read configs (with auto-refresh)
         ▼
┌─────────────────┐
│ Agent Container │
│  (Monitoring)   │
└─────────────────┘
```

## Key Features

### 🔄 Dynamic Configuration Refresh

The agent **automatically refreshes configuration** from Azure App Configuration at regular intervals (default: 5 minutes), enabling:
- Zero-downtime configuration updates
- No agent restarts required
- Fast policy changes propagation
- Seamless channel monitoring updates

See [Configuration Refresh Guide](./CONFIGURATION_REFRESH.md) for details.

## How It Works

### 1. Configuration Storage

- **Azure App Configuration**: Primary storage for runtime configuration
- **Local JSON files**: Fallback for local development

### 2. Configuration Keys

- `channels`: Stores the `channels.json` configuration
- `policies`: Stores the `policies.json` configuration

### 3. Authentication

Both containers use **Managed Identity** to authenticate to Azure App Configuration:
- No connection strings or keys required
- Automatic Azure AD authentication
- RBAC role: `App Configuration Data Reader`

### 4. Configuration Flow

#### Writing Configuration (UI):
1. User makes changes in Streamlit UI
2. UI calls `save_json_config(filename, config)`
3. Config is saved to both:
   - Azure App Configuration (primary)
   - Local file system (backup)

#### Reading Configuration (Agent):
1. Agent starts up
2. Calls `load_json_config(filename)`
3. Tries to read from Azure App Configuration first
4. Falls back to local files if App Configuration is unavailable
5. Loads configuration into memory

### 5. Configuration Refresh

Currently, the agent loads configuration at startup. To apply new configuration changes:

**Option 1: Restart Agent Container** (Current approach)
- Use Azure Portal, Azure CLI, or the provided script
- See [CONFIGURATION_RESTART.md](CONFIGURATION_RESTART.md)

**Option 2: Wait for next deployment** (Alternative)
- Configuration will reload when agent restarts
- Happens automatically during `azd up`

## Code Structure

### Configuration Loader (`src/utils/config_loader.py`)

```python
# Read configuration
def load_json_config(filename: str) -> dict[str, Any]:
    # 1. Try Azure App Configuration
    # 2. Fall back to local file
    
# Write configuration
def save_json_config(filename: str, config: dict[str, Any]) -> None:
    # 1. Write to Azure App Configuration
    # 2. Write to local file (backup)
```

### UI Integration (`ui/app.py`)

```python
from src.utils.config_loader import save_json_config

def save_channels_config(config):
    save_json_config("channels.json", config)
```

### Agent Integration (`src/main.py`)

```python
from .utils.config_loader import load_json_config

channels_config = load_json_config("channels.json")
policies_config = load_json_config("policies.json")
```

## Benefits

### ✅ Centralized Configuration
- Single source of truth
- No configuration drift between containers

### ✅ Persistence
- Configuration survives container restarts
- No data loss when containers are updated

### ✅ Scalability
- Multiple agent instances can share the same configuration
- Easy to add more containers that need access to config

### ✅ Security
- Managed Identity authentication
- No secrets in configuration files
- RBAC-based access control

### ✅ Fallback Support
- Works in local development without Azure resources
- Gracefully handles App Configuration outages

## Local Development

For local development without Azure App Configuration:

1. Configuration automatically falls back to local JSON files
2. No changes needed to your development workflow
3. Files are in `config/` directory:
   - `config/channels.json`
   - `config/policies.json`

## Troubleshooting

### Configuration changes not appearing

**Symptom**: Changed configuration in UI but agent behavior hasn't changed

**Solution**: Restart the agent container
```powershell
.\scripts\restart-agent.ps1
```

### App Configuration connection errors

**Symptom**: Errors like "Failed to load from App Configuration"

**Possible causes**:
1. Managed Identity not properly configured
2. RBAC role not assigned
3. App Configuration endpoint incorrect

**Check**:
```powershell
# Verify managed identity
az containerapp show --name <agent-name> --resource-group rg-azdteamsmod --query identity

# Verify RBAC assignments
az role assignment list --resource-group rg-azdteamsmod --query "[?principalId=='<principal-id>']"
```

### Fallback to local files

**Symptom**: Warning messages about falling back to local files

**This is normal** when:
- Running locally for development
- App Configuration is temporarily unavailable
- Testing with local configuration

## Future Enhancements

Potential improvements to the configuration system:

1. **Automatic Refresh**: Agent periodically reloads configuration without restart
2. **Change Notifications**: Azure Event Grid notifications for configuration changes
3. **Configuration Versioning**: Track and rollback configuration changes
4. **UI-based Restart**: Button in UI to restart agent automatically
5. **Configuration Validation**: Validate configuration before applying changes

## Related Documentation

- [Configuration Restart Guide](CONFIGURATION_RESTART.md)
- [Azure App Configuration Documentation](https://learn.microsoft.com/azure/azure-app-configuration/)
- [Managed Identity Documentation](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/)
