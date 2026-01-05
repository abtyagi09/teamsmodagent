# Simple Azure Container Apps Deployment Script
# Run this in a fresh PowerShell window

$ErrorActionPreference = "Stop"

Write-Host "Starting deployment..." -ForegroundColor Cyan

# Variables
$resourceGroup = "teams-mod-rg"
$envName = "teams-mod-env"

# Get registry info
Write-Host "Getting registry information..." -ForegroundColor Yellow
$registryName = (az acr list -g $resourceGroup --query "[0].name" -o tsv)
$acrUrl = "$registryName.azurecr.io"
$acrUsername = (az acr credential show -g $resourceGroup -n $registryName --query username -o tsv)
$acrPassword = (az acr credential show -g $resourceGroup -n $registryName --query "passwords[0].value" -o tsv)

Write-Host "Registry: $acrUrl" -ForegroundColor Green
Write-Host "Username: $acrUsername" -ForegroundColor Green

# Load .env file
Write-Host "Loading configuration from .env..." -ForegroundColor Yellow
$envVars = @{}
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $envVars[$matches[1]] = $matches[2]
    }
}

Write-Host "Configuration loaded" -ForegroundColor Green

# Deploy UI App
Write-Host ""
Write-Host "[1/2] Deploying UI App..." -ForegroundColor Cyan
Write-Host "This may take 2-3 minutes..."

az containerapp create `
    --name teams-mod-ui-app `
    --resource-group $resourceGroup `
    --environment $envName `
    --image "$acrUrl/teams-mod-ui:latest" `
    --target-port 8501 `
    --ingress external `
    --cpu 0.5 `
    --memory 1.0Gi `
    --min-replicas 1 `
    --max-replicas 5 `
    --registry-server $acrUrl `
    --registry-username $acrUsername `
    --registry-password $acrPassword `
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
        LOG_LEVEL=INFO

if ($LASTEXITCODE -ne 0) {
    Write-Host "UI App deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "UI App deployed successfully!" -ForegroundColor Green

# Deploy Agent App
Write-Host ""
Write-Host "[2/2] Deploying Monitoring Agent..." -ForegroundColor Cyan
Write-Host "This may take 2-3 minutes..."

az containerapp create `
    --name teams-mod-agent-app `
    --resource-group $resourceGroup `
    --environment $envName `
    --image "$acrUrl/teams-mod-agent:latest" `
    --cpu 0.5 `
    --memory 1.0Gi `
    --min-replicas 1 `
    --max-replicas 1 `
    --registry-server $acrUrl `
    --registry-username $acrUsername `
    --registry-password $acrPassword `
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
        LOG_LEVEL=INFO

if ($LASTEXITCODE -ne 0) {
    Write-Host "Agent App deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Agent App deployed successfully!" -ForegroundColor Green

# Get the URL
Write-Host ""
Write-Host "Getting UI URL..." -ForegroundColor Yellow
$uiUrl = (az containerapp show -n teams-mod-ui-app -g $resourceGroup --query "properties.configuration.ingress.fqdn" -o tsv)

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "UI Dashboard: https://$uiUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "To check status:" -ForegroundColor Yellow
Write-Host "  az containerapp list -g $resourceGroup -o table"
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "  az containerapp logs show -n teams-mod-ui-app -g $resourceGroup --follow"
Write-Host "  az containerapp logs show -n teams-mod-agent-app -g $resourceGroup --follow"
Write-Host ""
