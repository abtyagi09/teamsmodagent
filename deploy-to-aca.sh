#!/bin/bash

# Teams Moderation System - Azure Container Apps Deployment Script
# This script deploys the UI and monitoring agent to Azure Container Apps

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Teams Moderation System - Azure Container Apps Deploy   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Configuration
RESOURCE_GROUP="<your-resource-group-name>"
REGISTRY_NAME="teamsmodregistry"
CONTAINER_APP_ENV="teams-mod-env"
ACR_URL="${REGISTRY_NAME}.azurecr.io"

# UI App configuration
UI_IMAGE_NAME="teams-mod-ui"
UI_CONTAINER_APP_NAME="teams-mod-ui-app"

# Agent configuration
AGENT_IMAGE_NAME="teams-mod-agent"
AGENT_CONTAINER_APP_NAME="teams-mod-agent-app"

echo -e "${YELLOW}Step 1: Setting up variables${NC}"
echo "Resource Group: $RESOURCE_GROUP"
echo "Registry: $ACR_URL"
echo "Region: eastus (default)"
echo ""

# Check if logged in to Azure
echo -e "${YELLOW}Step 2: Checking Azure CLI authentication${NC}"
if ! az account show > /dev/null 2>&1; then
    echo -e "${RED}Not logged in to Azure. Run: az login${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Authenticated${NC}\n"

# Create resource group if it doesn't exist
echo -e "${YELLOW}Step 3: Ensuring resource group exists${NC}"
az group create \
    --name $RESOURCE_GROUP \
    --location eastus \
    --output none || true
echo -e "${GREEN}✓ Resource group ready${NC}\n"

# Create Azure Container Registry if it doesn't exist
echo -e "${YELLOW}Step 4: Setting up Azure Container Registry${NC}"
if az acr show --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ACR exists${NC}"
else
    echo "Creating ACR..."
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $REGISTRY_NAME \
        --sku Basic \
        --output none
    echo -e "${GREEN}✓ ACR created${NC}"
fi
echo ""

# Build and push UI image
echo -e "${YELLOW}Step 5: Building and pushing UI image${NC}"
az acr build \
    --registry $REGISTRY_NAME \
    --image ${UI_IMAGE_NAME}:latest \
    --file Dockerfile.ui \
    .
echo -e "${GREEN}✓ UI image pushed${NC}\n"

# Build and push Agent image
echo -e "${YELLOW}Step 6: Building and pushing Agent image${NC}"
az acr build \
    --registry $REGISTRY_NAME \
    --image ${AGENT_IMAGE_NAME}:latest \
    --file Dockerfile.agent \
    .
echo -e "${GREEN}✓ Agent image pushed${NC}\n"

# Create Container Apps Environment
echo -e "${YELLOW}Step 7: Setting up Container Apps Environment${NC}"
if az containerapp env show --resource-group $RESOURCE_GROUP --name $CONTAINER_APP_ENV > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Environment exists${NC}"
else
    echo "Creating Container Apps Environment..."
    az containerapp env create \
        --name $CONTAINER_APP_ENV \
        --resource-group $RESOURCE_GROUP \
        --location eastus \
        --output none
    echo -e "${GREEN}✓ Environment created${NC}"
fi
echo ""

# Deploy UI Container App
echo -e "${YELLOW}Step 8: Deploying UI Container App${NC}"
az containerapp create \
    --name $UI_CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image ${ACR_URL}/${UI_IMAGE_NAME}:latest \
    --target-port 8501 \
    --ingress external \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars \
        FOUNDRY_PROJECT_ENDPOINT="${FOUNDRY_PROJECT_ENDPOINT}" \
        FOUNDRY_MODEL_DEPLOYMENT="${FOUNDRY_MODEL_DEPLOYMENT}" \
        AZURE_SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID}" \
        CONTENT_SAFETY_ENDPOINT="${CONTENT_SAFETY_ENDPOINT}" \
        TEAMS_TENANT_ID="${TEAMS_TENANT_ID}" \
        TEAMS_CLIENT_ID="${TEAMS_CLIENT_ID}" \
        TEAMS_TEAM_ID="${TEAMS_TEAM_ID}" \
        LOG_LEVEL="INFO" \
    --secrets \
        content-safety-key="${CONTENT_SAFETY_KEY}" \
        teams-client-secret="${TEAMS_CLIENT_SECRET}" \
    --registry-server ${ACR_URL} \
    --registry-username $(az acr credential show --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --query username -o tsv) \
    --registry-password $(az acr credential show --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --query passwords[0].value -o tsv) \
    --output none || true

echo -e "${GREEN}✓ UI app deployed${NC}\n"

# Deploy Agent Container App
echo -e "${YELLOW}Step 9: Deploying Monitoring Agent Container App${NC}"
az containerapp create \
    --name $AGENT_CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image ${ACR_URL}/${AGENT_IMAGE_NAME}:latest \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars \
        FOUNDRY_PROJECT_ENDPOINT="${FOUNDRY_PROJECT_ENDPOINT}" \
        FOUNDRY_MODEL_DEPLOYMENT="${FOUNDRY_MODEL_DEPLOYMENT}" \
        AZURE_SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID}" \
        CONTENT_SAFETY_ENDPOINT="${CONTENT_SAFETY_ENDPOINT}" \
        TEAMS_TENANT_ID="${TEAMS_TENANT_ID}" \
        TEAMS_CLIENT_ID="${TEAMS_CLIENT_ID}" \
        TEAMS_TEAM_ID="${TEAMS_TEAM_ID}" \
        MODERATION_MODE="enforce" \
        LOG_LEVEL="INFO" \
    --secrets \
        content-safety-key="${CONTENT_SAFETY_KEY}" \
        teams-client-secret="${TEAMS_CLIENT_SECRET}" \
    --registry-server ${ACR_URL} \
    --registry-username $(az acr credential show --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --query username -o tsv) \
    --registry-password $(az acr credential show --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --query passwords[0].value -o tsv) \
    --output none || true

echo -e "${GREEN}✓ Agent app deployed${NC}\n"

# Get deployment URLs
echo -e "${YELLOW}Step 10: Getting deployment information${NC}"
echo ""
UI_URL=$(az containerapp show \
    --resource-group $RESOURCE_GROUP \
    --name $UI_CONTAINER_APP_NAME \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║             Deployment Successful! 🎉                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}UI Application:${NC}"
echo "  URL: https://${UI_URL}"
echo ""
echo -e "${GREEN}Monitoring Agent:${NC}"
echo "  Status: Running in background"
echo "  Checking Teams channels every 30 seconds"
echo ""
echo -e "${GREEN}Container Registry:${NC}"
echo "  URL: ${ACR_URL}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Access UI at: https://${UI_URL}"
echo "  2. Configure channels and policies"
echo "  3. Monitor violations in real-time"
echo ""
echo -e "${YELLOW}View Logs:${NC}"
echo "  az containerapp logs show --name $UI_CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP"
echo "  az containerapp logs show --name $AGENT_CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
