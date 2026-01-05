# Azure Container Apps Deployment Script
# Run this to deploy your Teams Moderation System

$ErrorActionPreference = "Stop"

# Configuration
$resourceGroup = "teams-mod-rg"
$registryName = "teamsmod69668"
$envName = "teams-mod-env"
$region = "eastus"

Write-Host "`n=== Starting Deployment ===" -ForegroundColor Green

# Step 1: Get ACR credentials
Write-Host "`n[1/5] Getting Container Registry credentials..." -ForegroundColor Yellow
$acrUrl = "$registryName.azurecr.io"
$acrUsername = az acr credential show --resource-group $resourceGroup --name $registryName --query username -o tsv
$acrPassword = az acr credential show --resource-group $resourceGroup --name $registryName --query "passwords[0].value" -o tsv
Write-Host "Registry: $acrUrl" -ForegroundColor Cyan

# Step 2: Load environment variables from .env
Write-Host "`n[2/5] Loading configuration from .env..." -ForegroundColor Yellow
$envVars = @{}
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $envVars[$matches[1]] = $matches[2]
    }
}
Write-Host "Loaded $($envVars.Count) configuration values" -ForegroundColor Cyan

# Step 3: Create Container Apps Environment
Write-Host "`n[3/5] Creating Container Apps Environment..." -ForegroundColor Yellow
Write-Host "(This takes 2-3 minutes...)" -ForegroundColor Gray
az containerapp env create `
    --name $envName `
    --resource-group $resourceGroup `
    --location $region `
    --output none
Write-Host "Environment created!" -ForegroundColor Green

# Step 4: Deploy UI App
Write-Host "`n[4/5] Deploying UI Container App..." -ForegroundColor Yellow
Write-Host "(This takes 1-2 minutes...)" -ForegroundColor Gray

az containerapp create `
    --name "teams-mod-ui-app" `
    --resource-group $resourceGroup `
    --environment $envName `
    --image "$acrUrl/teams-mod-ui:latest" `
    --target-port 8501 `
    --ingress external `
    --cpu 0.5 `
    --memory 1.0Gi `
    --min-replicas 1 `
    --max-replicas 5 `
    --env-vars `
        FOUNDRY_PROJECT_ENDPOINT="$($envVars['FOUNDRY_PROJECT_ENDPOINT'])" `
        FOUNDRY_MODEL_DEPLOYMENT="$($envVars['FOUNDRY_MODEL_DEPLOYMENT'])" `
        AZURE_SUBSCRIPTION_ID="$($envVars['AZURE_SUBSCRIPTION_ID'])" `
        CONTENT_SAFETY_ENDPOINT="$($envVars['CONTENT_SAFETY_ENDPOINT'])" `
        CONTENT_SAFETY_KEY="$($envVars['CONTENT_SAFETY_KEY'])" `
        TEAMS_TENANT_ID="$($envVars['TEAMS_TENANT_ID'])" `
        TEAMS_CLIENT_ID="$($envVars['TEAMS_CLIENT_ID'])" `
        TEAMS_CLIENT_SECRET="$($envVars['TEAMS_CLIENT_SECRET'])" `
        TEAMS_TEAM_ID="$($envVars['TEAMS_TEAM_ID'])" `
        LOG_LEVEL=INFO `
    --registry-server $acrUrl `
    --registry-username $acrUsername `
    --registry-password $acrPassword `
    --output none

Write-Host "UI app deployed!" -ForegroundColor Green

# Step 5: Deploy Monitoring Agent
Write-Host "`n[5/5] Deploying Monitoring Agent..." -ForegroundColor Yellow
Write-Host "(This takes 1-2 minutes...)" -ForegroundColor Gray

az containerapp create `
    --name "teams-mod-agent-app" `
    --resource-group $resourceGroup `
    --environment $envName `
    --image "$acrUrl/teams-mod-agent:latest" `
    --cpu 0.5 `
    --memory 1.0Gi `
    --min-replicas 1 `
    --max-replicas 1 `
    --env-vars `
        FOUNDRY_PROJECT_ENDPOINT="$($envVars['FOUNDRY_PROJECT_ENDPOINT'])" `
        FOUNDRY_MODEL_DEPLOYMENT="$($envVars['FOUNDRY_MODEL_DEPLOYMENT'])" `
        AZURE_SUBSCRIPTION_ID="$($envVars['AZURE_SUBSCRIPTION_ID'])" `
        CONTENT_SAFETY_ENDPOINT="$($envVars['CONTENT_SAFETY_ENDPOINT'])" `
        CONTENT_SAFETY_KEY="$($envVars['CONTENT_SAFETY_KEY'])" `
        TEAMS_TENANT_ID="$($envVars['TEAMS_TENANT_ID'])" `
        TEAMS_CLIENT_ID="$($envVars['TEAMS_CLIENT_ID'])" `
        TEAMS_CLIENT_SECRET="$($envVars['TEAMS_CLIENT_SECRET'])" `
        TEAMS_TEAM_ID="$($envVars['TEAMS_TEAM_ID'])" `
        MODERATION_MODE=enforce `
        LOG_LEVEL=INFO `
    --registry-server $acrUrl `
    --registry-username $acrUsername `
    --registry-password $acrPassword `
    --output none

Write-Host "Agent deployed!" -ForegroundColor Green

# Get URL
Write-Host "`n=== Deployment Complete! ===" -ForegroundColor Green
Start-Sleep -Seconds 5

$uiUrl = az containerapp show `
    --name "teams-mod-ui-app" `
    --resource-group $resourceGroup `
    --query "properties.configuration.ingress.fqdn" `
    -o tsv

Write-Host "`nYour Teams Moderation System is ready!" -ForegroundColor Cyan
Write-Host "`nUI Dashboard: https://$uiUrl" -ForegroundColor Yellow
Write-Host "Resource Group: $resourceGroup" -ForegroundColor Gray

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Open https://$uiUrl in your browser"
Write-Host "  2. Configure channels to monitor"
Write-Host "  3. Review and adjust moderation policies"

Write-Host "`nView Logs:" -ForegroundColor Yellow
Write-Host "  az containerapp logs show --name teams-mod-ui-app --resource-group $resourceGroup --follow"
Write-Host "  az containerapp logs show --name teams-mod-agent-app --resource-group $resourceGroup --follow"

Write-Host "`n"
