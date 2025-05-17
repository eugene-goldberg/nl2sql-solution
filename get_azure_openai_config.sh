#!/bin/bash

echo "Finding Azure OpenAI resources..."
echo "================================"

# List all Azure OpenAI resources
echo "Available Azure OpenAI resources:"
az cognitiveservices account list --query "[?kind=='OpenAI'].{Name:name, ResourceGroup:resourceGroup, Location:location}" -o table

echo ""
echo "To get configuration for a specific Azure OpenAI resource:"
echo "Replace <resource-name> and <resource-group> with your values"
echo ""

# Example commands to get specific resource details
echo "# Get API Key:"
echo "az cognitiveservices account keys list --name <resource-name> --resource-group <resource-group> --query key1 -o tsv"
echo ""

echo "# Get Endpoint:"
echo "az cognitiveservices account show --name <resource-name> --resource-group <resource-group> --query properties.endpoint -o tsv"
echo ""

echo "# List deployments in your Azure OpenAI resource:"
echo "az cognitiveservices account deployment list --name <resource-name> --resource-group <resource-group> --query \"[].{DeploymentName:name, Model:properties.model.name, Version:properties.model.version}\" -o table"
echo ""

echo "# Recommended API version for this solution:"
echo "AZURE_OPENAI_API_VERSION=2023-07-01-preview"