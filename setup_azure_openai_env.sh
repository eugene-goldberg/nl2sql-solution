#!/bin/bash

# Script to help retrieve Azure OpenAI configuration values

echo "Azure OpenAI Configuration Helper"
echo "================================"

# Check if user is logged in
az account show > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Please login to Azure CLI first: az login"
    exit 1
fi

# Get all Azure OpenAI resources
echo "Searching for Azure OpenAI resources..."
resources=$(az cognitiveservices account list --query "[?kind=='OpenAI']" -o json)

if [ -z "$resources" ] || [ "$resources" == "[]" ]; then
    echo "No Azure OpenAI resources found in your subscription."
    echo ""
    echo "To create an Azure OpenAI resource:"
    echo "az cognitiveservices account create --name <resource-name> --resource-group <rg-name> --kind OpenAI --sku S0 --location <location>"
    exit 1
fi

# Display available resources
echo ""
echo "Available Azure OpenAI resources:"
echo "$resources" | jq -r '.[] | "\(.name) (Resource Group: \(.resourceGroup), Location: \(.location))"'

echo ""
read -p "Enter the name of your Azure OpenAI resource: " resource_name
read -p "Enter the resource group name: " resource_group

# Get the configuration values
echo ""
echo "Retrieving configuration..."

# Get API Key
api_key=$(az cognitiveservices account keys list --name "$resource_name" --resource-group "$resource_group" --query key1 -o tsv 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "Error: Could not retrieve API key. Please check resource name and resource group."
    exit 1
fi

# Get Endpoint
endpoint=$(az cognitiveservices account show --name "$resource_name" --resource-group "$resource_group" --query properties.endpoint -o tsv)

# Get deployments
echo ""
echo "Available deployments:"
az cognitiveservices account deployment list --name "$resource_name" --resource-group "$resource_group" --query "[].{DeploymentName:name, Model:properties.model.name, Version:properties.model.version}" -o table

echo ""
read -p "Enter your deployment name from the list above: " deployment_name

# Create .env file
env_file="/workspaces/codespaces-blank/NL2SQL-Solution-1/config/.env"
echo ""
echo "Creating $env_file with Azure OpenAI configuration..."

cat > "$env_file" << EOF
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=$api_key
AZURE_OPENAI_ENDPOINT=$endpoint
AZURE_OPENAI_API_VERSION=2023-07-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=$deployment_name

# Azure SQL Database Configuration
AZURE_SQL_CONNECTION_STRING=YOUR_AZURE_SQL_CONNECTION_STRING

# LangChain Configuration (Optional for tracing)
LANGCHAIN_API_KEY=YOUR_LANGCHAIN_API_KEY
LANGCHAIN_TRACING_V2=true

# Database Configuration
INCLUDED_TABLES=table1,table2,table3
READ_ONLY=true  # Set to 'false' to allow write operations (not recommended)
EOF

echo ""
echo "Configuration saved to $env_file"
echo ""
echo "Next steps:"
echo "1. Update AZURE_SQL_CONNECTION_STRING with your database connection string"
echo "2. Update INCLUDED_TABLES with the tables you want to expose"
echo "3. (Optional) Add LANGCHAIN_API_KEY for tracing"
echo ""
echo "Your Azure OpenAI configuration:"
echo "================================"
echo "AZURE_OPENAI_API_KEY=$api_key"
echo "AZURE_OPENAI_ENDPOINT=$endpoint"
echo "AZURE_OPENAI_API_VERSION=2023-07-01-preview"
echo "AZURE_OPENAI_DEPLOYMENT_NAME=$deployment_name"