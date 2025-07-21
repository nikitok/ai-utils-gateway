#!/bin/bash

# Deploy script for staging/alfa environment
# This ensures the deployment is named directual-ui-alfa

cd "$(dirname "$0")"

echo "Updating Helm dependencies..."
helm dependency update

echo "Deploying to alfa namespace..."
# Use release name 'directual-ui-alfa' which becomes the deployment name directly
helm -n alfa upgrade --install directual-ai-utils . \
  --create-namespace \
  --wait

echo "Deployment complete!"
echo "Deployment name: directual-ai-utils "