#!/bin/bash

# Check if Railway CLI is installed
if ! [ -x "$(command -v railway)" ]; then
  echo "Railway CLI is not installed. Please run railway-setup.sh first."
  exit 1
fi

# Check if project is linked
if ! [ -f ".railway" ]; then
  echo "No Railway project linked. Please run railway-setup.sh first."
  exit 1
fi

# Deploy the project to Railway
echo "Deploying project to Railway..."

# Deploy the project
railway up

echo "Deployment complete!"
