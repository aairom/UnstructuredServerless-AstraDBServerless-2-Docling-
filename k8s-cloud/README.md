# IBM Cloud Code Engine Deployment Guide

This directory contains all necessary files to deploy the PDF to AstraDB GUI application on IBM Cloud Code Engine Serverless Fleets.

## 📁 Files Overview

```
k8s-cloud/
├── Dockerfile              # Container image definition
├── .dockerignore          # Files to exclude from Docker build
├── application.yaml       # Code Engine application manifest
├── secrets.yaml           # Kubernetes secrets template
├── configmap.yaml         # Application configuration
├── deploy.sh              # Automated deployment script
└── README.md              # This file
```

## 🎯 Prerequisites

### Required Tools
- [IBM Cloud CLI](https://cloud.ibm.com/docs/cli)
- [Docker](https://docs.docker.com/get-docker/)
- [Code Engine Plugin](https://cloud.ibm.com/docs/codeengine?topic=codeengine-cli)

### Required Credentials
- **IBM Cloud Account** with Code Engine access
- **AstraDB Credentials**:
  - API Endpoint
  - Application Token
- **OpenAI API Key**

### Install IBM Cloud CLI and Plugins

```bash
# Install IBM Cloud CLI (macOS)
curl -fsSL https://clis.cloud.ibm.com/install/osx | sh

# Install Code Engine plugin
ibmcloud plugin install code-engine

# Verify installation
ibmcloud ce version
```

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# Set environment variables
export ASTRADB_API_ENDPOINT="https://your-database-id-region.apps.astra.datastax.com"
export ASTRADB_TOKEN="AstraCS:xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Optional: Customize deployment
export CODE_ENGINE_PROJECT="pdf-astradb-project"
export CONTAINER_REGISTRY="us.icr.io"
export REGISTRY_NAMESPACE="your-namespace"

# Run deployment script
cd k8s-cloud
./deploy.sh
```

The script will:
1. ✅ Check prerequisites
2. ✅ Login to IBM Cloud
3. ✅ Create/select Code Engine project
4. ✅ Build Docker image
5. ✅ Push to IBM Container Registry
6. ✅ Create secrets
7. ✅ Deploy application
8. ✅ Display application URL

### Option 2: Manual Deployment

#### Step 1: Login to IBM Cloud

```bash
# Login with SSO
ibmcloud login --sso

# Or with API key
ibmcloud login --apikey @/path/to/apikey.json

# Target region
ibmcloud target -r us-south
```

#### Step 2: Create Code Engine Project

```bash
# Create project
ibmcloud ce project create --name pdf-astradb-project

# Select project
ibmcloud ce project select --name pdf-astradb-project
```

#### Step 3: Build and Push Docker Image

```bash
# Login to Container Registry
ibmcloud cr login

# Create namespace (if needed)
ibmcloud cr namespace-add your-namespace

# Build image
cd ..
docker build -f k8s-cloud/Dockerfile -t us.icr.io/your-namespace/pdf-astradb-gui:latest .

# Push image
docker push us.icr.io/your-namespace/pdf-astradb-gui:latest
```

#### Step 4: Create Secrets

```bash
# Create AstraDB credentials
ibmcloud ce secret create --name astradb-credentials \
  --from-literal api-endpoint="YOUR_ASTRADB_API_ENDPOINT" \
  --from-literal application-token="YOUR_ASTRADB_TOKEN"

# Create OpenAI credentials
ibmcloud ce secret create --name openai-credentials \
  --from-literal api-key="YOUR_OPENAI_API_KEY"
```

#### Step 5: Deploy Application

```bash
# Create application
ibmcloud ce app create --name pdf-astradb-gui \
  --image us.icr.io/your-namespace/pdf-astradb-gui:latest \
  --port 8080 \
  --min-scale 0 \
  --max-scale 10 \
  --cpu 0.5 \
  --memory 1G \
  --ephemeral-storage 2G \
  --env-from-secret astradb-credentials \
  --env-from-secret openai-credentials \
  --env PORT=8080
```

#### Step 6: Get Application URL

```bash
# Get application details
ibmcloud ce app get --name pdf-astradb-gui

# Get URL only
ibmcloud ce app get --name pdf-astradb-gui --output url
```

## 📊 Application Configuration

### Resource Allocation

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 0.5 cores | 2 cores |
| Memory | 1 GB | 4 GB |
| Storage | 2 GB | 4 GB |

### Scaling Configuration

- **Min Scale**: 0 (scale to zero when idle)
- **Max Scale**: 10 instances
- **Concurrency**: 100 requests per instance
- **Target**: 80% concurrency utilization

### Environment Variables

Set via secrets:
- `API_ENDPOINT` - AstraDB API endpoint
- `APPLICATION_TOKEN` - AstraDB token
- `OPENAI_API_KEY` - OpenAI API key

Set directly:
- `PORT` - Application port (8080)
- `PYTHONUNBUFFERED` - Python output buffering (1)

## 🔧 Management Commands

### View Application Status

```bash
# Get application details
ibmcloud ce app get --name pdf-astradb-gui

# List all applications
ibmcloud ce app list
```

### View Logs

```bash
# Stream logs
ibmcloud ce app logs --name pdf-astradb-gui --follow

# Get recent logs
ibmcloud ce app logs --name pdf-astradb-gui --tail 100
```

### Update Application

```bash
# Update image
ibmcloud ce app update --name pdf-astradb-gui \
  --image us.icr.io/your-namespace/pdf-astradb-gui:v2

# Update resources
ibmcloud ce app update --name pdf-astradb-gui \
  --cpu 1 \
  --memory 2G

# Update scaling
ibmcloud ce app update --name pdf-astradb-gui \
  --min-scale 1 \
  --max-scale 20
```

### Update Secrets

```bash
# Update AstraDB credentials
ibmcloud ce secret update --name astradb-credentials \
  --from-literal api-endpoint="NEW_ENDPOINT" \
  --from-literal application-token="NEW_TOKEN"

# Update OpenAI credentials
ibmcloud ce secret update --name openai-credentials \
  --from-literal api-key="NEW_API_KEY"
```

### Delete Application

```bash
# Delete application
ibmcloud ce app delete --name pdf-astradb-gui

# Delete secrets
ibmcloud ce secret delete --name astradb-credentials
ibmcloud ce secret delete --name openai-credentials

# Delete project
ibmcloud ce project delete --name pdf-astradb-project
```

## 🔍 Troubleshooting

### Application Won't Start

```bash
# Check application events
ibmcloud ce app events --name pdf-astradb-gui

# Check logs for errors
ibmcloud ce app logs --name pdf-astradb-gui --tail 50

# Verify secrets exist
ibmcloud ce secret list
```

### Image Pull Errors

```bash
# Verify image exists
ibmcloud cr image-list

# Check registry access
ibmcloud cr login

# Verify namespace
ibmcloud cr namespace-list
```

### Connection Issues

```bash
# Test application endpoint
curl https://your-app-url.appdomain.cloud/_stcore/health

# Check application status
ibmcloud ce app get --name pdf-astradb-gui
```

### Secret Issues

```bash
# List secrets
ibmcloud ce secret list

# Get secret details (values are hidden)
ibmcloud ce secret get --name astradb-credentials

# Recreate secret if needed
ibmcloud ce secret delete --name astradb-credentials
ibmcloud ce secret create --name astradb-credentials \
  --from-literal api-endpoint="..." \
  --from-literal application-token="..."
```

## 📈 Monitoring

### View Metrics

```bash
# Get application metrics
ibmcloud ce app get --name pdf-astradb-gui --output json

# Monitor scaling
watch -n 5 'ibmcloud ce app get --name pdf-astradb-gui | grep -A 5 "Status"'
```

### Cost Optimization

The application is configured to:
- **Scale to zero** when idle (no cost when not in use)
- **Auto-scale** based on demand
- **Optimize resources** for typical workloads

Estimated costs:
- Idle: $0/month (scaled to zero)
- Light usage: $5-10/month
- Moderate usage: $20-50/month

## 🔐 Security Best Practices

1. **Use Secrets** for all sensitive data
2. **Rotate credentials** regularly
3. **Enable XSRF protection** (configured in Dockerfile)
4. **Use HTTPS** (automatic with Code Engine)
5. **Limit access** with IAM policies
6. **Monitor logs** for suspicious activity

## 🌐 Custom Domain (Optional)

```bash
# Add custom domain
ibmcloud ce app update --name pdf-astradb-gui \
  --domain your-domain.com

# Configure DNS
# Add CNAME record pointing to Code Engine URL
```

## 📚 Additional Resources

- [IBM Cloud Code Engine Documentation](https://cloud.ibm.com/docs/codeengine)
- [Code Engine CLI Reference](https://cloud.ibm.com/docs/codeengine?topic=codeengine-cli)
- [Serverless Fleets Tutorial](https://github.com/IBM/CodeEngine/blob/main/serverless-fleets/tutorials/docling/README.md)
- [Code Engine Samples](https://github.com/IBM/CodeEngine/tree/main/serverless-fleets)

## 🆘 Support

For issues:
1. Check application logs
2. Review Code Engine documentation
3. Verify credentials and configuration
4. Contact IBM Cloud support

## 📝 Notes

- Application uses Streamlit on port 8080
- Health check endpoint: `/_stcore/health`
- Supports scale-to-zero for cost optimization
- Automatic HTTPS with Code Engine domains
- Built-in load balancing and auto-scaling

---

**Ready to deploy on IBM Cloud Code Engine! 🚀**