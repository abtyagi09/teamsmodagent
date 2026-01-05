# End-to-End Testing Guide

This guide walks through complete system testing from configuration to execution.

## Pre-Testing Checklist

Before testing, ensure you have:

- [ ] `.env` file created with actual Azure credentials
- [ ] Teams app registration with permissions granted
- [ ] At least one Teams channel to monitor
- [ ] Streamlit installed (`pip install streamlit`)
- [ ] All dependencies installed (`pip install -r requirements.txt`)

## Phase 1: Configuration Testing (5 minutes)

### Step 1.1: Launch Configuration UI

```powershell
streamlit run ui/app.py
```

Expected: Browser opens at `http://localhost:8501`

### Step 1.2: Run Connection Tests

1. Click "🔍 Test Connection" in sidebar
2. Click "Run Connection Tests" button
3. Verify all tests pass:
   - ✅ Environment Configuration
   - ✅ Configuration Files
   - ✅ Python Dependencies
   - ✅ File System Access

**If tests fail:** Check the error messages and fix issues before proceeding.

### Step 1.3: Configure Channels

1. Go to "📺 Channel Settings"
2. Add a test channel:
   - Enter channel name (e.g., "general" or "test-moderation")
   - Click "Add Monitored Channel"
3. Verify channel appears in the list
4. Save monitoring settings (enable real-time monitoring)

### Step 1.4: Configure Policies

1. Go to "📋 Moderation Policies"
2. For testing, enable at least:
   - **Hate Speech**: Enabled, Medium threshold, Flag action
   - **Profanity**: Enabled, High threshold, Flag action
3. Set notifications to your preference
4. Save each policy

**Note:** Use "Flag" action for testing to avoid deleting real messages.

## Phase 2: Environment Validation (2 minutes)

### Step 2.1: Create .env File

If not already created:

```powershell
# Copy from example
copy .env.example .env

# Edit with your values
notepad .env
```

Fill in the missing values:
- `TEAMS_CLIENT_ID`
- `TEAMS_CLIENT_SECRET`
- `TEAMS_TEAM_ID`
- `AZURE_RESOURCE_GROUP`

### Step 2.2: Run Verification Script

```powershell
python scripts/verify_setup.py
```

Expected output:
```
✅ Environment Configuration
✅ Microsoft Foundry Configuration
✅ Azure AI Content Safety Configuration
✅ Microsoft Teams Configuration
✅ Channel Configuration
✅ Policy Configuration
```

**If verification fails:** Address the specific issues reported.

## Phase 3: Dry-Run Testing (5 minutes)

### Step 3.1: Test Basic Execution

```powershell
python src/main.py --dry-run --log-level DEBUG
```

This will:
- Connect to Teams Graph API
- Fetch recent messages from configured channels
- Analyze content using Content Safety + AI
- **NOT delete** any messages (dry-run mode)
- Log all actions

**Expected output:**
```
[INFO] Starting Teams Moderation System
[INFO] Dry-run mode enabled - no messages will be deleted
[INFO] Loading configuration...
[INFO] Connecting to Teams...
[INFO] Monitoring channels: ['general']
[INFO] Starting workflow...
```

### Step 3.2: Monitor the Output

Watch for:
- ✅ Successful Teams connection
- ✅ Channel messages retrieved
- ✅ Content Safety API calls
- ✅ AI agent analysis
- ✅ Policy evaluation results

**Common issues:**

**Error: Authentication failed**
- Check TEAMS_CLIENT_ID, TEAMS_CLIENT_SECRET, TEAMS_TENANT_ID
- Verify app permissions are granted in Azure Portal

**Error: Channel not found**
- Verify TEAMS_TEAM_ID is correct
- Check channel names in channels.json match actual Teams channels

**Error: Content Safety connection failed**
- Verify CONTENT_SAFETY_ENDPOINT and CONTENT_SAFETY_KEY
- Check Azure Content Safety resource is active

### Step 3.3: Test Specific Channel

```powershell
python src/main.py --dry-run --channel general
```

This monitors only the "general" channel.

## Phase 4: Content Testing (10 minutes)

### Step 4.1: Post Test Messages

In your Teams channel, post various test messages:

**Test 1: Clean Message**
```
Hello everyone! Looking forward to our team meeting today.
```

**Test 2: Mild Profanity**
```
This dang printer is not working again!
```

**Test 3: Policy Violation (Testing)**
```
I really hate this stupid project, everyone is incompetent!
```

**Test 4: PII Test**
```
My SSN is 123-45-6789 and my email is john.doe@email.com
```

### Step 4.2: Run Moderation

```powershell
python src/main.py --dry-run --log-level DEBUG
```

### Step 4.3: Review Results

Check the console output for each message:

```
[INFO] Analyzing message: "Hello everyone..."
[INFO] Content Safety: severity=0 (safe)
[INFO] AI Analysis: No violations detected
[INFO] Action: allow

[INFO] Analyzing message: "I really hate this..."
[WARNING] Content Safety: severity=4 (hate_speech)
[WARNING] AI Analysis: Detected hate_speech - confidence: high
[WARNING] Policy violated: hate_speech
[INFO] Action (dry-run): would flag message
```

### Step 4.4: Review Logs

```powershell
# View structured logs
Get-Content logs/moderation.log -Tail 50

# Or open in notepad
notepad logs/moderation.log
```

Look for:
- Message IDs processed
- Policy violations detected
- Actions that would be taken
- AI reasoning for decisions

## Phase 5: Policy Tuning (5 minutes)

### Step 5.1: Analyze False Positives

Review the dry-run results:
- Were any safe messages flagged incorrectly?
- Were violations missed?

### Step 5.2: Adjust Thresholds

Open the UI again:

```powershell
streamlit run ui/app.py
```

Go to "Moderation Policies" and adjust:

**If too many false positives:**
- Increase threshold: `medium` → `high`
- Or change action: `delete` → `flag`

**If violations are missed:**
- Decrease threshold: `high` → `medium`
- Enable more policies

### Step 5.3: Re-test

```powershell
python src/main.py --dry-run
```

Verify the adjustments improved accuracy.

## Phase 6: Enforce Mode Testing (CAUTION)

⚠️ **WARNING:** This will actually delete messages in Teams!

### Step 6.1: Update .env

```powershell
notepad .env
```

Change:
```
MODERATION_MODE=monitor
```
To:
```
MODERATION_MODE=enforce
```

### Step 6.2: Test on a Dedicated Channel

**IMPORTANT:** Create a test channel first!

1. In Teams, create a channel called "test-moderation"
2. Update channels.json:

```powershell
streamlit run ui/app.py
```

- Remove other channels from monitoring
- Add only "test-moderation"

### Step 6.3: Post a Test Violation

In the "test-moderation" channel, post:
```
This is a test violation message that should be deleted.
I hate everyone and this is violent content for testing.
```

### Step 6.4: Run in Enforce Mode

```powershell
python src/main.py --channel test-moderation --log-level DEBUG
```

### Step 6.5: Verify Deletion

1. Check Teams - the message should be deleted (if policy action is "delete")
2. Check logs for confirmation:
   ```
   [WARNING] Policy violated: hate_speech
   [INFO] Executing action: delete
   [INFO] Message deleted successfully
   [INFO] Notification sent to: hr@russellcellular.com
   ```

### Step 6.6: Check Notifications

If you configured webhooks or email:
- Check webhook channel for admin notifications
- Verify notification content includes violation details

## Phase 7: Continuous Monitoring Test (10 minutes)

### Step 7.1: Start Continuous Monitoring

```powershell
# Monitor mode (safe for testing)
$env:MODERATION_MODE="monitor"
python src/main.py --log-level INFO
```

This will:
- Poll Teams every 60 seconds (POLLING_INTERVAL)
- Continuously check for new messages
- Log all activity
- Keep running until you stop it (Ctrl+C)

### Step 7.2: Post Messages During Monitoring

While the script is running:
1. Post a clean message in Teams
2. Wait ~60 seconds
3. Check console - message should be analyzed
4. Post a violation
5. Wait ~60 seconds
6. Check console - violation should be detected

### Step 7.3: Monitor Performance

Watch for:
- ✅ Consistent polling every 60 seconds
- ✅ Quick analysis (< 5 seconds per message)
- ✅ No errors or crashes
- ✅ Memory usage stable

### Step 7.4: Stop Monitoring

Press `Ctrl+C` to gracefully stop.

Expected:
```
[INFO] Shutdown signal received
[INFO] Cleaning up resources...
[INFO] Shutdown complete
```

## Phase 8: Production Readiness Check

### Step 8.1: Review Configuration

```powershell
streamlit run ui/app.py
```

Go to "System Settings" and verify:
- ✅ All Azure endpoints configured
- ✅ Teams credentials valid
- ✅ Notification settings correct

### Step 8.2: Final Verification

```powershell
python scripts/verify_setup.py
```

All checks should pass.

### Step 8.3: Set Production Policies

In the UI:
1. Go to "Moderation Policies"
2. Set appropriate thresholds for production:
   - **Hate Speech**: Medium, Delete, Notify
   - **Violence**: Medium, Delete, Notify
   - **Self Harm**: Low, Delete, Notify
   - **Profanity**: High, Flag, No notify
   - **PII Leak**: Low, Flag, Notify

3. Go to "Channel Settings"
4. Add all production channels to monitor
5. Add sensitive channels to exclude (e.g., "hr-private", "executives")

### Step 8.4: Update .env for Production

```powershell
notepad .env
```

Set:
```
LOG_LEVEL=INFO
MODERATION_MODE=enforce
POLLING_INTERVAL=60
```

## Phase 9: Deployment Testing (Optional)

If deploying to Azure:

### Step 9.1: Build Docker Image

```powershell
docker build -t teams-moderation:test .
```

### Step 9.2: Test Container Locally

```powershell
docker run --env-file .env teams-moderation:test
```

### Step 9.3: Deploy to Azure Container Apps

Follow [deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md)

## Troubleshooting Common Issues

### Issue: "ModuleNotFoundError: No module named 'agent_framework'"

**Solution:**
```powershell
pip install agent-framework-azure-ai --pre
```

### Issue: "Authentication failed to Teams"

**Solution:**
1. Verify app registration in Azure Portal
2. Check permissions: ChannelMessage.Read.All, ChannelMessage.Delete
3. Ensure admin consent granted
4. Verify CLIENT_ID and CLIENT_SECRET are correct

### Issue: "Content Safety API error"

**Solution:**
1. Check CONTENT_SAFETY_KEY is valid
2. Verify endpoint URL format
3. Ensure Content Safety resource is in same region
4. Check Azure subscription has quota

### Issue: "No messages detected"

**Solution:**
1. Verify TEAMS_TEAM_ID is correct
2. Check channel names match exactly (case-sensitive)
3. Ensure there are recent messages (within polling window)
4. Check app has permissions to read messages

### Issue: "Policies not working as expected"

**Solution:**
1. Review threshold settings (try lowering)
2. Check policy is enabled
3. Verify action is not "allow"
4. Review AI analysis reasoning in logs
5. Consider false positive rate vs. sensitivity

## Success Criteria

Your system is ready for production when:

- ✅ All connection tests pass
- ✅ Dry-run detects violations correctly
- ✅ False positive rate is acceptable (< 5%)
- ✅ Messages are deleted/flagged as expected
- ✅ Notifications are received
- ✅ Continuous monitoring runs stable
- ✅ Logs are clean (no errors)
- ✅ Performance is acceptable (< 5 sec per message)

## Next Steps

After successful testing:

1. **Document your configuration**: Note which policies work best
2. **Train your team**: Show HR how to review flagged content
3. **Monitor for 1 week**: Run in "flag" mode before switching to "delete"
4. **Adjust policies**: Fine-tune based on real-world results
5. **Set up alerts**: Configure Azure Monitor for the container
6. **Schedule reviews**: Weekly check of moderation logs

## Getting Help

If you encounter issues:

1. Check logs: `logs/moderation.log`
2. Run verification: `python scripts/verify_setup.py`
3. Review documentation: `README.md`, `ARCHITECTURE.md`
4. Check Azure Portal for service health
5. Verify Teams app permissions

## Testing Checklist

Print this checklist and check off each item:

- [ ] Phase 1: Configuration UI tested
- [ ] Phase 2: Environment validated
- [ ] Phase 3: Dry-run successful
- [ ] Phase 4: Content testing completed
- [ ] Phase 5: Policies tuned
- [ ] Phase 6: Enforce mode tested (in test channel)
- [ ] Phase 7: Continuous monitoring stable
- [ ] Phase 8: Production ready
- [ ] Phase 9: Deployment tested (if applicable)

**Date tested:** _____________
**Tested by:** _____________
**Notes:** _____________
