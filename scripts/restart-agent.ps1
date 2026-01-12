#!/usr/bin/env pwsh
# Script to restart the agent container app after configuration changes

param(
    [string]$ResourceGroup = "rg-azdteamsmod"
)

Write-Host "🔍 Finding agent container app..." -ForegroundColor Cyan

# Get the agent container app name
$containerAppName = az containerapp list `
    --resource-group $ResourceGroup `
    --query "[?contains(name, 'ca-agent')].name" `
    -o tsv

if (-not $containerAppName) {
    Write-Host "❌ Agent container app not found in resource group: $ResourceGroup" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found agent: $containerAppName" -ForegroundColor Green

# Get the active revision
Write-Host "🔍 Getting active revision..." -ForegroundColor Cyan
$revision = az containerapp revision list `
    --name $containerAppName `
    --resource-group $ResourceGroup `
    --query "[?properties.active].name" `
    -o tsv

if (-not $revision) {
    Write-Host "❌ No active revision found" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Active revision: $revision" -ForegroundColor Green

# Restart the container
Write-Host "🔄 Restarting agent container..." -ForegroundColor Cyan
az containerapp revision restart `
    --name $containerAppName `
    --resource-group $ResourceGroup `
    --revision $revision

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Agent container restarted successfully!" -ForegroundColor Green
    Write-Host "ℹ️  Configuration changes will take effect shortly" -ForegroundColor Blue
} else {
    Write-Host "❌ Failed to restart agent container" -ForegroundColor Red
    exit 1
}
