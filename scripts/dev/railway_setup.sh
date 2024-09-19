#!/bin/bash

# Check if Railway CLI is installed
if ! [ -x "$(command -v railway)" ]; then
  echo "Railway CLI is not installed. Installing..."
  # npm install -g @railway/cli
  brew install railway
else
  echo "Railway CLI is already installed."
fi

# Login to Railway
# echo "Logging into Railway..."
# railway login --browserless

# Create a new project
read -p "Enter a name for your new Railway project: " project_name
railway init

# Set the region (Railway doesn't have a direct way to set region via CLI)
echo "Note: Railway automatically selects the best region. You can change it later in the web dashboard."

# Set environment variables
echo "Setting environment variables..."
railway variables add DEVPI_USER="$DEVPI_USER"
railway variables add DEVPI_PASSWORD="$DEVPI_PASSWORD"
railway variables add DEVPI_KAOSMAPS_USER="$DEVPI_KAOSMAPS_USER"
railway variables add DEVPI_KAOSMAPS_PASSWORD="$DEVPI_KAOSMAPS_PASSWORD"
railway variables add DEVPI_INDEX="$DEVPI_INDEX"

echo "Railway project setup complete!"

# Update railway.toml with values from .env
# python scripts/update_railway_toml.py

# Optional: Deploy the project
read -p "Do you want to deploy the project now? (y/n) " deploy_now
if [[ $deploy_now == "y" || $deploy_now == "Y" ]]; then
  railway up
  echo "Deployment complete!"
else
  echo "You can deploy later using 'railway up' command."
fi

