#!/bin/bash

# Deployment script for IBM Cloud Code Engine
# This script builds and deploys the PDF to AstraDB GUI application

set -e

echo "=========================================="
echo "IBM Cloud Code Engine Deployment"
echo "PDF to AstraDB GUI Application"
echo "=========================================="
echo ""

# Configuration
PROJECT_NAME="${CODE_ENGINE_PROJECT:-pdf-astradb-project}"
APP_NAME="pdf-astradb-gui"
REGISTRY="${CONTAINER_REGISTRY:-us.icr.io}"
NAMESPACE="${REGISTRY_NAMESPACE:-default}"
IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${APP_NAME}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v ibmcloud &> /dev/null; then
    echo "❌ IBM Cloud CLI not found. Please install it first."
    echo "   https://cloud.ibm.com/docs/cli"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Login to IBM Cloud
echo "🔐 Logging in to IBM Cloud..."
ibmcloud login --sso || ibmcloud login

# Target Code Engine
echo "🎯 Targeting Code Engine..."
ibmcloud target -r us-south  # Change region as needed
ibmcloud plugin install code-engine

# Select or create project
echo "📦 Setting up Code Engine project..."
if ibmcloud ce project list | grep -q "$PROJECT_NAME"; then
    echo "   Using existing project: $PROJECT_NAME"
    ibmcloud ce project select --name "$PROJECT_NAME"
else
    echo "   Creating new project: $PROJECT_NAME"
    ibmcloud ce project create --name "$PROJECT_NAME"
    ibmcloud ce project select --name "$PROJECT_NAME"
fi

# Login to Container Registry
echo "🐳 Logging in to IBM Container Registry..."
ibmcloud cr login

# Create namespace if it doesn't exist
echo "📁 Setting up registry namespace..."
if ! ibmcloud cr namespace-list | grep -q "$NAMESPACE"; then
    echo "   Creating namespace: $NAMESPACE"
    ibmcloud cr namespace-add "$NAMESPACE"
fi

# Build and push Docker image
echo "🏗️  Building Docker image..."
cd "$(dirname "$0")/.."
docker build -f k8s-cloud/Dockerfile -t "${IMAGE_NAME}:${IMAGE_TAG}" .

echo "📤 Pushing image to registry..."
docker push "${IMAGE_NAME}:${IMAGE_TAG}"

echo "✅ Image pushed: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Create secrets
echo "🔑 Creating secrets..."

# Check if secrets exist
if ibmcloud ce secret get --name astradb-credentials &> /dev/null; then
    echo "   Updating AstraDB credentials..."
    ibmcloud ce secret update --name astradb-credentials \
        --from-literal api-endpoint="${ASTRADB_API_ENDPOINT}" \
        --from-literal application-token="${ASTRADB_TOKEN}"
else
    echo "   Creating AstraDB credentials..."
    ibmcloud ce secret create --name astradb-credentials \
        --from-literal api-endpoint="${ASTRADB_API_ENDPOINT}" \
        --from-literal application-token="${ASTRADB_TOKEN}"
fi

if ibmcloud ce secret get --name openai-credentials &> /dev/null; then
    echo "   Updating OpenAI credentials..."
    ibmcloud ce secret update --name openai-credentials \
        --from-literal api-key="${OPENAI_API_KEY}"
else
    echo "   Creating OpenAI credentials..."
    ibmcloud ce secret create --name openai-credentials \
        --from-literal api-key="${OPENAI_API_KEY}"
fi

echo "✅ Secrets configured"
echo ""

# Deploy or update application
echo "🚀 Deploying application..."

if ibmcloud ce app get --name "$APP_NAME" &> /dev/null; then
    echo "   Updating existing application..."
    ibmcloud ce app update --name "$APP_NAME" \
        --image "${IMAGE_NAME}:${IMAGE_TAG}" \
        --port 8080 \
        --min-scale 0 \
        --max-scale 10 \
        --cpu 0.5 \
        --memory 1G \
        --ephemeral-storage 2G \
        --env-from-secret astradb-credentials \
        --env-from-secret openai-credentials \
        --env PORT=8080
else
    echo "   Creating new application..."
    ibmcloud ce app create --name "$APP_NAME" \
        --image "${IMAGE_NAME}:${IMAGE_TAG}" \
        --port 8080 \
        --min-scale 0 \
        --max-scale 10 \
        --cpu 0.5 \
        --memory 1G \
        --ephemeral-storage 2G \
        --env-from-secret astradb-credentials \
        --env-from-secret openai-credentials \
        --env PORT=8080
fi

# Wait for deployment
echo "⏳ Waiting for deployment to complete..."
sleep 10

# Get application URL
APP_URL=$(ibmcloud ce app get --name "$APP_NAME" --output json | grep -o '"url":"[^"]*' | cut -d'"' -f4)

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "📊 Application Details:"
echo "   - Name: $APP_NAME"
echo "   - Project: $PROJECT_NAME"
echo "   - Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "🌐 Access your application at:"
echo "   $APP_URL"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: ibmcloud ce app logs --name $APP_NAME"
echo "   - Get status: ibmcloud ce app get --name $APP_NAME"
echo "   - Update app: ibmcloud ce app update --name $APP_NAME"
echo "   - Delete app: ibmcloud ce app delete --name $APP_NAME"
echo ""

# Made with Bob
