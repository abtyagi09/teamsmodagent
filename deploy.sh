#!/bin/bash

# Teams Moderation - Azure Deployment Script

set -e

echo ""
echo "=== Teams Moderation - Azure Container Apps Setup ==="
echo ""

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "[ERROR] Azure CLI not found"
    echo "Install from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

echo "[Step 1] Validating Azure CLI..."
az --version | head -1

# Check login
echo "[Step 2] Checking Azure login..."
if ! az account show > /dev/null 2>&1; then
    echo "[ERROR] Not logged into Azure. Run: az login"
    exit 1
fi

ACCOUNT=$(az account show --query 'user.name' -o tsv)
SUBSCRIPTION=$(az account show --query 'name' -o tsv)
echo "[OK] Logged in as: $ACCOUNT ($SUBSCRIPTION)"

# Gather config
echo ""
echo "[Step 3] Gathering configuration..."
read -p "Resource Group name (default: teams-mod-rg): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-teams-mod-rg}

read -p "Azure region (default: eastus): " REGION
REGION=${REGION:-eastus}

echo "[OK] Resource Group: $RESOURCE_GROUP"
echo "[OK] Region: $REGION"

# Create resource group
echo ""
echo "[Step 4] Creating resource group..."
az group create --name $RESOURCE_GROUP --location $REGION --output none
echo "[OK] Resource group ready"

# Get environment variables
echo ""
echo "[Step 5] Collecting environment variables..."
echo "Get these values from your .env file:"
echo ""

read -p "FOUNDRY_PROJECT_ENDPOINT: " FOUNDRY_PROJECT_ENDPOINT
read -p "FOUNDRY_MODEL_DEPLOYMENT: " FOUNDRY_MODEL_DEPLOYMENT
read -p "AZURE_SUBSCRIPTION_ID: " AZURE_SUBSCRIPTION_ID
read -p "CONTENT_SAFETY_ENDPOINT: " CONTENT_SAFETY_ENDPOINT
read -sp "CONTENT_SAFETY_KEY: " CONTENT_SAFETY_KEY
echo ""
read -p "TEAMS_TENANT_ID: " TEAMS_TENANT_ID
read -p "TEAMS_CLIENT_ID: " TEAMS_CLIENT_ID
read -sp "TEAMS_CLIENT_SECRET: " TEAMS_CLIENT_SECRET
echo ""
read -p "TEAMS_TEAM_ID: " TEAMS_TEAM_ID

echo "[OK] Configuration collected"

# Create container registry
echo ""
echo "[Step 6] Setting up Azure Container Registry..."
REGISTRY_NAME="teamsmod$((RANDOM % 10000 + 10000))"
echo "Registry name: $REGISTRY_NAME"

az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic --output none
echo "[OK] Container Registry created"

# Build images
echo ""
echo "[Step 7] Building and pushing container images..."
echo "Building UI image..."
az acr build --registry $REGISTRY_NAME --image "teams-mod-ui:latest" --file "Dockerfile.ui" . --output none
echo "[OK] UI image pushed"

echo "Building Agent image..."
az acr build --registry $REGISTRY_NAME --image "teams-mod-agent:latest" --file "Dockerfile.agent" . --output none
echo "[OK] Agent image pushed"

# Create Container Apps environment
echo ""
echo "[Step 8] Creating Container Apps environment..."
ENV_NAME="teams-mod-env"
az containerapp env create --name $ENV_NAME --resource-group $RESOURCE_GROUP --location $REGION --output none
echo "[OK] Container Apps environment created"

# Get ACR credentials
echo ""
echo "[Step 9] Getting container registry credentials..."
ACR_USERNAME=$(az acr credential show --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --query "passwords[0].value" -o tsv)
ACR_URL="$REGISTRY_NAME.azurecr.io"
echo "[OK] ACR credentials obtained"

# Deploy UI app
echo ""
echo "[Step 10] Deploying UI Container App..."
az containerapp create \
    --name "teams-mod-ui-app" \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --image "$ACR_URL/teams-mod-ui:latest" \
    --target-port 8501 \
    --ingress external \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars \
        "FOUNDRY_PROJECT_ENDPOINT=$FOUNDRY_PROJECT_ENDPOINT" \
        "FOUNDRY_MODEL_DEPLOYMENT=$FOUNDRY_MODEL_DEPLOYMENT" \
        "AZURE_SUBSCRIPTION_ID=$AZURE_SUBSCRIPTION_ID" \
        "CONTENT_SAFETY_ENDPOINT=$CONTENT_SAFETY_ENDPOINT" \
        "TEAMS_TENANT_ID=$TEAMS_TENANT_ID" \
        "TEAMS_CLIENT_ID=$TEAMS_CLIENT_ID" \
        "TEAMS_TEAM_ID=$TEAMS_TEAM_ID" \
        "LOG_LEVEL=INFO" \
    --secrets \
        "content-safety-key=$CONTENT_SAFETY_KEY" \
        "teams-client-secret=$TEAMS_CLIENT_SECRET" \
    --registry-server $ACR_URL \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --output none

echo "[OK] UI app deployed"

# Deploy Agent app
echo ""
echo "[Step 11] Deploying Monitoring Agent..."
az containerapp create \
    --name "teams-mod-agent-app" \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --image "$ACR_URL/teams-mod-agent:latest" \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars \
        "FOUNDRY_PROJECT_ENDPOINT=$FOUNDRY_PROJECT_ENDPOINT" \
        "FOUNDRY_MODEL_DEPLOYMENT=$FOUNDRY_MODEL_DEPLOYMENT" \
        "AZURE_SUBSCRIPTION_ID=$AZURE_SUBSCRIPTION_ID" \
        "CONTENT_SAFETY_ENDPOINT=$CONTENT_SAFETY_ENDPOINT" \
        "TEAMS_TENANT_ID=$TEAMS_TENANT_ID" \
        "TEAMS_CLIENT_ID=$TEAMS_CLIENT_ID" \
        "TEAMS_TEAM_ID=$TEAMS_TEAM_ID" \
        "MODERATION_MODE=enforce" \
        "LOG_LEVEL=INFO" \
    --secrets \
        "content-safety-key=$CONTENT_SAFETY_KEY" \
        "teams-client-secret=$TEAMS_CLIENT_SECRET" \
    --registry-server $ACR_URL \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --output none

echo "[OK] Agent app deployed"

# Get URLs
echo ""
echo "[Step 12] Getting deployment URLs..."
sleep 15

UI_URL=$(az containerapp show --name "teams-mod-ui-app" --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv)

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "[Access Your Applications]"
echo "  UI Dashboard:  https://$UI_URL"
echo "  Region:        $REGION"
echo "  Resource Group: $RESOURCE_GROUP"
echo ""
echo "[System Components]"
echo "  - UI App (Streamlit)      | Auto-scaling: 1-5 replicas"
echo "  - Monitoring Agent        | Always running in background"
echo "  - Container Registry      | Storing your images"
echo "  - Container Apps Env      | Managed infrastructure"
echo ""
echo "[Next Steps]"
echo "  1. Open UI: https://$UI_URL"
echo "  2. Configure channels and policies"
echo "  3. Monitor violations in real-time"
echo ""
echo "[View Logs]"
echo "  UI logs:"
echo "    az containerapp logs show --name teams-mod-ui-app --resource-group $RESOURCE_GROUP"
echo ""
echo "  Agent logs:"
echo "    az containerapp logs show --name teams-mod-agent-app --resource-group $RESOURCE_GROUP"
echo ""
echo "[Cost Estimate]"
echo "  Container Apps (both):  ~$40-60/month"
echo "  Container Registry:     ~$5/month"
echo "  Total:                  ~$45-75/month"
echo ""
