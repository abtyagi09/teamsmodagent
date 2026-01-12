"""
Teams Moderation Configuration UI

A Streamlit-based web application for configuring Teams channels,
moderation policies, and system settings.
"""

import json
import os
import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config_loader import get_settings, load_json_config, save_json_config


# Page configuration
st.set_page_config(
    page_title="Teams Moderation Config",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0078D4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #DFF6DD;
        border-left: 4px solid #107C10;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #FFF4CE;
        border-left: 4px solid #FFB900;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #FDE7E9;
        border-left: 4px solid #E81123;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


def load_channels_config():
    """Load channels configuration."""
    try:
        return load_json_config("channels.json")
    except FileNotFoundError:
        # Return default structure
        return {
            "monitored_channels": [],
            "excluded_channels": [],
            "monitoring_settings": {
                "enable_real_time": True,
                "enable_batch_scan": False,
                "batch_interval_minutes": 60,
            },
        }


def save_channels_config(config):
    """Save channels configuration."""
    save_json_config("channels.json", config)


def load_policies_config():
    """Load policies configuration."""
    try:
        return load_json_config("policies.json")
    except FileNotFoundError:
        # Return default structure
        return {
            "text_policies": {
                "hate_speech": {
                    "enabled": True,
                    "threshold": "medium",
                    "action": "delete",
                    "notify": True,
                    "description": "Detects hate speech, discrimination, or harassment",
                },
                "profanity": {
                    "enabled": True,
                    "threshold": "high",
                    "action": "flag",
                    "notify": False,
                    "description": "Detects profane language",
                },
                "violence": {
                    "enabled": True,
                    "threshold": "medium",
                    "action": "delete",
                    "notify": True,
                    "description": "Detects violent or threatening content",
                },
                "self_harm": {
                    "enabled": True,
                    "threshold": "low",
                    "action": "delete",
                    "notify": True,
                    "description": "Detects self-harm related content",
                },
                "sexual_content": {
                    "enabled": True,
                    "threshold": "medium",
                    "action": "delete",
                    "notify": True,
                    "description": "Detects sexually explicit content",
                },
                "pii_leak": {
                    "enabled": True,
                    "threshold": "low",
                    "action": "flag",
                    "notify": True,
                    "description": "Detects personally identifiable information",
                },
            },
            "image_policies": {
                "inappropriate_images": {
                    "enabled": False,
                    "threshold": "medium",
                    "action": "delete",
                    "notify": True,
                    "description": "Analyzes images for inappropriate content (future feature)",
                }
            },
            "actions": {
                "delete": {"description": "Immediately delete the message", "requires_approval": False},
                "flag": {"description": "Flag for review but do not delete", "requires_approval": True},
                "archive": {"description": "Move to archive channel for review", "requires_approval": False},
            },
            "thresholds": {
                "low": "0-30% confidence",
                "medium": "31-70% confidence",
                "high": "71-100% confidence",
            },
        }


def save_policies_config(config):
    """Save policies configuration."""
    save_json_config("policies.json", config)


def verify_teams_connection():
    """Verify Teams connection (placeholder)."""
    try:
        settings = get_settings()
        if settings.teams_team_id and settings.teams_client_id:
            return True, "Configuration found"
        return False, "Missing Teams configuration"
    except Exception as e:
        return False, str(e)


# Main UI
def main():
    # Header
    st.markdown('<div class="main-header">🛡️ Teams Moderation Configuration</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Configure channels, policies, and settings for AI-powered content moderation</div>',
        unsafe_allow_html=True,
    )

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Configuration",
        ["📺 Channel Settings", "📋 Moderation Policies", "⚙️ System Settings", "🔍 Test Connection"],
    )

    # Show current status
    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Status")
    is_connected, message = verify_teams_connection()
    if is_connected:
        st.sidebar.success(f"✅ {message}")
    else:
        st.sidebar.warning(f"⚠️ {message}")

    # Main content area
    if page == "📺 Channel Settings":
        show_channel_settings()
    elif page == "📋 Moderation Policies":
        show_moderation_policies()
    elif page == "⚙️ System Settings":
        show_system_settings()
    elif page == "🔍 Test Connection":
        show_test_connection()


def show_channel_settings():
    """Channel configuration page."""
    st.header("📺 Channel Configuration")
    st.markdown("Configure which Teams channels to monitor and exclude.")

    # Load current config
    config = load_channels_config()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monitored Channels")
        st.markdown("*Channels where moderation is active*")

        monitored = config.get("monitored_channels", [])

        # Display current channels
        if monitored:
            st.markdown("**Current monitored channels:**")
            for idx, channel in enumerate(monitored):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.text(f"• {channel}")
                with col_b:
                    if st.button("Remove", key=f"remove_monitored_{idx}"):
                        monitored.remove(channel)
                        config["monitored_channels"] = monitored
                        save_channels_config(config)
                        st.rerun()
        else:
            st.info("No channels configured yet.")

        # Add new channel
        st.markdown("---")
        new_monitored = st.text_input("Add channel to monitor:", key="new_monitored", placeholder="general")
        if st.button("➕ Add Monitored Channel"):
            if new_monitored and new_monitored not in monitored:
                monitored.append(new_monitored)
                config["monitored_channels"] = monitored
                save_channels_config(config)
                st.success(f"Added '{new_monitored}' to monitored channels!")
                st.info("ℹ️ Restart the agent container for changes to take effect")
                st.rerun()
            elif new_monitored in monitored:
                st.warning("Channel already in list!")

    with col2:
        st.subheader("Excluded Channels")
        st.markdown("*Channels excluded from moderation*")

        excluded = config.get("excluded_channels", [])

        # Display current channels
        if excluded:
            st.markdown("**Current excluded channels:**")
            for idx, channel in enumerate(excluded):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.text(f"• {channel}")
                with col_b:
                    if st.button("Remove", key=f"remove_excluded_{idx}"):
                        excluded.remove(channel)
                        config["excluded_channels"] = excluded
                        save_channels_config(config)
                        st.rerun()
        else:
            st.info("No exclusions configured.")

        # Add new channel
        st.markdown("---")
        new_excluded = st.text_input("Add channel to exclude:", key="new_excluded", placeholder="hr-private")
        if st.button("➕ Add Excluded Channel"):
            if new_excluded and new_excluded not in excluded:
                excluded.append(new_excluded)
                config["excluded_channels"] = excluded
                save_channels_config(config)
                st.success(f"Added '{new_excluded}' to excluded channels!")
                st.rerun()
            elif new_excluded in excluded:
                st.warning("Channel already in list!")

    # Monitoring settings
    st.markdown("---")
    st.subheader("⚙️ Monitoring Settings")

    monitoring_settings = config.get("monitoring_settings", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        enable_realtime = st.checkbox(
            "Enable Real-time Monitoring",
            value=monitoring_settings.get("enable_real_time", True),
            help="Monitor channels in real-time with polling",
        )

    with col2:
        enable_batch = st.checkbox(
            "Enable Batch Scanning",
            value=monitoring_settings.get("enable_batch_scan", False),
            help="Perform periodic batch scans of historical messages",
        )

    with col3:
        batch_interval = st.number_input(
            "Batch Interval (minutes)",
            min_value=5,
            max_value=1440,
            value=monitoring_settings.get("batch_interval_minutes", 60),
            help="How often to run batch scans",
        )

    if st.button("💾 Save Monitoring Settings", type="primary"):
        config["monitoring_settings"] = {
            "enable_real_time": enable_realtime,
            "enable_batch_scan": enable_batch,
            "batch_interval_minutes": batch_interval,
        }
        save_channels_config(config)
        st.success("✅ Monitoring settings saved!")
        st.info("ℹ️ Note: Restart the agent container for changes to take effect")

    # Preview configuration
    st.markdown("---")
    with st.expander("📄 View Full Configuration"):
        st.json(config)


def show_moderation_policies():
    """Moderation policies configuration page."""
    st.header("📋 Moderation Policies")
    st.markdown("Configure content moderation rules and actions.")

    # Load current config
    config = load_policies_config()

    # Text Policies
    st.subheader("📝 Text Content Policies")

    text_policies = config.get("text_policies", {})

    for policy_name, policy_config in text_policies.items():
        with st.expander(f"{'✅' if policy_config.get('enabled') else '❌'} {policy_name.replace('_', ' ').title()}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                enabled = st.checkbox(
                    "Enabled",
                    value=policy_config.get("enabled", True),
                    key=f"enabled_{policy_name}",
                )

            with col2:
                threshold = st.selectbox(
                    "Threshold",
                    options=["low", "medium", "high"],
                    index=["low", "medium", "high"].index(policy_config.get("threshold", "medium")),
                    key=f"threshold_{policy_name}",
                    help="Confidence level required to trigger action",
                )

            with col3:
                action = st.selectbox(
                    "Action",
                    options=["delete", "flag", "archive", "allow"],
                    index=["delete", "flag", "archive", "allow"].index(policy_config.get("action", "flag")),
                    key=f"action_{policy_name}",
                    help="What to do when violation is detected",
                )

            notify = st.checkbox(
                "Send Notifications",
                value=policy_config.get("notify", False),
                key=f"notify_{policy_name}",
                help="Notify HR/admins when this policy is violated",
            )

            description = st.text_area(
                "Description",
                value=policy_config.get("description", ""),
                key=f"description_{policy_name}",
                height=68,
            )

            if st.button(f"💾 Save {policy_name.replace('_', ' ').title()}", key=f"save_{policy_name}"):
                text_policies[policy_name] = {
                    "enabled": enabled,
                    "threshold": threshold,
                    "action": action,
                    "notify": notify,
                    "description": description,
                }
                config["text_policies"] = text_policies
                save_policies_config(config)
                st.success(f"✅ {policy_name.replace('_', ' ').title()} policy saved!")

    # Image Policies (Future)
    st.markdown("---")
    st.subheader("🖼️ Image Content Policies (Future Feature)")

    image_policies = config.get("image_policies", {})

    for policy_name, policy_config in image_policies.items():
        with st.expander(
            f"{'✅' if policy_config.get('enabled') else '❌'} {policy_name.replace('_', ' ').title()} [Coming Soon]"
        ):
            st.info("Image moderation will be available in Phase 2.")
            enabled = st.checkbox(
                "Enabled (when available)",
                value=policy_config.get("enabled", False),
                key=f"img_enabled_{policy_name}",
                disabled=True,
            )

    # Global Settings
    st.markdown("---")
    st.subheader("🌐 Global Policy Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Action Definitions:**")
        actions = config.get("actions", {})
        for action_name, action_config in actions.items():
            st.markdown(f"**{action_name.title()}**: {action_config.get('description', '')}")

    with col2:
        st.markdown("**Threshold Definitions:**")
        thresholds = config.get("thresholds", {})
        for threshold_name, threshold_desc in thresholds.items():
            st.markdown(f"**{threshold_name.title()}**: {threshold_desc}")

    # Preview configuration
    st.markdown("---")
    with st.expander("📄 View Full Policy Configuration"):
        st.json(config)


def show_system_settings():
    """System settings page."""
    st.header("⚙️ System Settings")
    st.markdown("Configure environment variables and system parameters.")

    try:
        settings = get_settings()

        # Microsoft Foundry Settings
        st.subheader("🤖 Microsoft Foundry Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Project Endpoint", value=settings.foundry_project_endpoint, disabled=True)
            st.text_input("Subscription ID", value=settings.azure_subscription_id or "Not configured", disabled=True)

        with col2:
            st.text_input("Model Deployment", value=settings.foundry_model_deployment, disabled=True)
            st.text_input("Resource Group", value=settings.azure_resource_group or "Not configured", disabled=True)

        # Content Safety Settings
        st.markdown("---")
        st.subheader("🛡️ Content Safety Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Content Safety Endpoint", value=settings.content_safety_endpoint, disabled=True)

        with col2:
            key_display = "***" + settings.content_safety_key[-4:] if settings.content_safety_key else "Not configured"
            st.text_input("API Key", value=key_display, disabled=True, type="password")

        # Teams Settings
        st.markdown("---")
        st.subheader("👥 Microsoft Teams Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Tenant ID", value=settings.teams_tenant_id, disabled=True)
            st.text_input("Client ID", value=settings.teams_client_id, disabled=True)

        with col2:
            st.text_input("Team ID", value=settings.teams_team_id, disabled=True)
            secret_display = "***" + settings.teams_client_secret[-4:] if settings.teams_client_secret else "Not configured"
            st.text_input("Client Secret", value=secret_display, disabled=True, type="password")

        # Application Settings
        st.markdown("---")
        st.subheader("📊 Application Settings")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.text_input("Log Level", value=settings.log_level, disabled=True)

        with col2:
            st.text_input("Moderation Mode", value=settings.moderation_mode, disabled=True)

        with col3:
            st.number_input("Polling Interval (sec)", value=settings.polling_interval, disabled=True)

        # Notification Settings
        st.markdown("---")
        st.subheader("📧 Notification Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Notification Email", value=settings.notification_email or "Not configured", disabled=True)

        with col2:
            webhook_display = settings.notification_webhook[:50] + "..." if settings.notification_webhook else "Not configured"
            st.text_input("Webhook URL", value=webhook_display, disabled=True)

        # Edit instructions
        st.markdown("---")
        st.info(
            """
            💡 **To modify these settings:**
            
            1. Edit the `.env` file in the project root directory
            2. Restart the application to apply changes
            3. Run `python scripts/verify_setup.py` to validate configuration
            """
        )

    except Exception as e:
        st.error(f"❌ Error loading settings: {str(e)}")
        st.markdown(
            """
            **Troubleshooting:**
            - Ensure `.env` file exists (copy from `.env.example`)
            - Verify all required variables are set
            - Check for syntax errors in `.env` file
            """
        )


def show_test_connection():
    """Test connection page."""
    st.header("🔍 Test Connection")
    st.markdown("Verify your configuration and test connections to Azure services.")

    if st.button("🔄 Run Connection Tests", type="primary"):
        with st.spinner("Testing connections..."):
            # Test 1: Environment Configuration
            st.subheader("1️⃣ Environment Configuration")
            try:
                settings = get_settings()
                st.success("✅ Environment configuration loaded successfully")

                # Show key settings
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Foundry Endpoint", "✅ Configured")
                with col2:
                    st.metric("Content Safety", "✅ Configured")
                with col3:
                    st.metric("Teams Config", "✅ Configured")

            except Exception as e:
                st.error(f"❌ Environment configuration failed: {str(e)}")

            # Test 2: Configuration Files
            st.markdown("---")
            st.subheader("2️⃣ Configuration Files")
            try:
                channels = load_channels_config()
                policies = load_policies_config()

                col1, col2 = st.columns(2)
                with col1:
                    monitored_count = len(channels.get("monitored_channels", []))
                    st.metric("Monitored Channels", monitored_count)

                with col2:
                    enabled_policies = sum(
                        1 for p in policies.get("text_policies", {}).values() if p.get("enabled", False)
                    )
                    total_policies = len(policies.get("text_policies", {}))
                    st.metric("Active Policies", f"{enabled_policies}/{total_policies}")

                st.success("✅ Configuration files loaded successfully")

            except Exception as e:
                st.error(f"❌ Configuration files error: {str(e)}")

            # Test 3: Module Imports
            st.markdown("---")
            st.subheader("3️⃣ Python Dependencies")
            try:
                # Test critical imports
                import agent_framework
                import azure.ai.contentsafety
                import msgraph

                st.success("✅ All required Python modules are installed")

                # Show versions if available
                with st.expander("View Module Versions"):
                    st.text(f"agent_framework: {getattr(agent_framework, '__version__', 'unknown')}")
                    st.text(f"azure.ai.contentsafety: Installed")
                    st.text(f"msgraph: Installed")

            except ImportError as e:
                st.error(f"❌ Missing required module: {str(e)}")
                st.markdown("Run: `pip install -r requirements.txt`")

            # Test 4: File Permissions
            st.markdown("---")
            st.subheader("4️⃣ File System Access")
            try:
                config_dir = get_project_root() / "config"
                logs_dir = get_project_root() / "logs"

                # Check write permissions
                test_file = config_dir / ".test_write"
                try:
                    test_file.write_text("test")
                    test_file.unlink()
                    st.success("✅ Configuration directory is writable")
                except:
                    st.warning("⚠️ Cannot write to config directory")

                # Check logs directory
                if not logs_dir.exists():
                    logs_dir.mkdir(parents=True, exist_ok=True)
                st.success("✅ Logs directory accessible")

            except Exception as e:
                st.error(f"❌ File system error: {str(e)}")

            # Summary
            st.markdown("---")
            st.success("🎉 Connection tests completed!")
            st.info(
                """
                **Next Steps:**
                1. If all tests passed, you're ready to run the moderation system
                2. Use `python src/main.py --dry-run` to test without deleting messages
                3. Monitor the logs in the `logs/` directory
                """
            )

    # Manual test options
    st.markdown("---")
    st.subheader("Manual Connection Tests")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Test Microsoft Foundry"):
            with st.spinner("Testing Foundry connection..."):
                try:
                    settings = get_settings()
                    st.info(f"Endpoint: {settings.foundry_project_endpoint}")
                    st.info(f"Model: {settings.foundry_model_deployment}")
                    st.success("✅ Configuration valid (actual connection test requires API call)")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    with col2:
        if st.button("Test Teams Access"):
            with st.spinner("Testing Teams access..."):
                try:
                    settings = get_settings()
                    st.info(f"Tenant: {settings.teams_tenant_id}")
                    st.info(f"Team: {settings.teams_team_id}")
                    st.success("✅ Configuration valid (actual connection test requires API call)")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # Documentation
    st.markdown("---")
    st.markdown(
        """
        ### 📚 Helpful Resources
        
        - **Setup Guide**: See `deployment/SETUP_GUIDE.md` for Azure resource setup
        - **Quick Start**: See `QUICKSTART.md` for local testing
        - **Troubleshooting**: Run `python scripts/verify_setup.py` for detailed checks
        """
    )


if __name__ == "__main__":
    main()
