# Getting Started with NL2SQL Solution

This document provides a complete guide to setting up and running the NL2SQL solution that translates natural language queries to SQL using Semantic Kernel, LangChain, and Azure OpenAI.

## Prerequisites

1. **Python 3.11 or later**
2. **Docker** (for running SQL Server locally)
3. **Azure Account** with:
   - Azure OpenAI Service resource
   - A deployed language model (e.g., GPT-3.5-Turbo)
4. **Azure CLI** installed and configured (`az login`)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd NL2SQL-Solution-1

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set Up SQL Server

```bash
# Run SQL Server in Docker
docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=Kpss1s0k' \
  -p 1433:1433 --name sql_server \
  -d mcr.microsoft.com/mssql/server:2019-latest

# Import Northwind database
docker cp Northwind_instnwnd.sql sql_server:/tmp/
docker exec -it sql_server /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P Kpss1s0k \
  -i /tmp/Northwind_instnwnd.sql
```

### 3. Install ODBC Driver

```bash
# Add Microsoft repository
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" | \
  sudo tee /etc/apt/sources.list.d/mssql-release.list

# Install driver
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Verify installation
odbcinst -q -d
# Should show: [ODBC Driver 18 for SQL Server]
```

### 4. Configure Azure OpenAI

```bash
# Find your Azure OpenAI resources
az cognitiveservices account list --query "[?kind=='OpenAI']" -o table

# Get API key
az cognitiveservices account keys list \
  --name <your-resource-name> \
  --resource-group <your-resource-group> \
  --query key1 -o tsv

# Get endpoint
az cognitiveservices account show \
  --name <your-resource-name> \
  --resource-group <your-resource-group> \
  --query properties.endpoint -o tsv

# List deployments
az cognitiveservices account deployment list \
  --name <your-resource-name> \
  --resource-group <your-resource-group> \
  --query "[].{Name:name, Model:properties.model.name}" -o table
```

### 5. Create Configuration

Create `config/.env` file:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-07-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>

# SQL Server Configuration (Local Docker)
AZURE_SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=localhost;Database=Northwind;Uid=sa;Pwd=Kpss1s0k;TrustServerCertificate=yes;

# LangChain Configuration (Optional)
LANGCHAIN_TRACING_V2=false

# Database Configuration
INCLUDED_TABLES=Employees,Categories,Customers,Shippers,Suppliers,Orders,Products,Order Details
READ_ONLY=true
```

### 6. Run the Solution

```bash
# Run simple example
python examples/simple_example.py

# Run test script
python examples/test_nl2sql.py

# Run demo
python demo.py
```

## Example Queries

Try these natural language queries:
- "What are the top 5 customers by order total?"
- "Show me all employees who are in the Sales department"
- "What is the average product price by category?"
- "List all products that are out of stock"
- "Show me orders shipped to France in 1997"

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  User Query     │ --> │ Semantic Kernel  │ --> │ NL2SQL Plugin   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          |
                                                          v
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   SQL Server    │ <-- │ LangChain Agent  │ <-- │ Azure OpenAI    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Key Components

1. **Semantic Kernel**: Orchestrates the AI workflow
2. **NL2SQL Plugin**: Bridges Semantic Kernel and LangChain
3. **LangChain SQL Agent**: Handles SQL generation and execution
4. **Azure OpenAI**: Provides natural language understanding
5. **SQL Server**: Stores and queries the data

## Troubleshooting

### Common Issues

1. **ODBC Driver Not Found**
   ```bash
   # Verify installation
   odbcinst -q -d
   ```

2. **Token Limit Exceeded**
   - Check if IMAGE/NTEXT columns are filtered
   - Reduce INCLUDED_TABLES in .env

3. **Connection Refused**
   - Ensure SQL Server container is running
   - Check port 1433 is accessible

4. **LangSmith Warnings**
   - Set `LANGCHAIN_TRACING_V2=false` in .env

## Advanced Configuration

### Custom Table Selection

Edit `INCLUDED_TABLES` in .env to control which tables are exposed:
```env
INCLUDED_TABLES=Customers,Orders,Products
```

### Enable Write Operations

⚠️ **Use with caution**
```env
READ_ONLY=false
```

### Include Binary Columns

For models with higher token limits:
```python
register_nl2sql_plugin(
    kernel=kernel,
    include_image_columns=True
)
```

## Security Best Practices

1. Always use read-only database users in production
2. Implement rate limiting for API calls
3. Validate and sanitize all user inputs
4. Log all queries for audit purposes
5. Use secrets management for credentials

## Next Steps

1. Deploy to Azure App Service or Container Instances
2. Add a web interface using Streamlit or Gradio
3. Implement query result caching
4. Add support for multiple databases
5. Create custom prompts for domain-specific queries

## Resources

- [Semantic Kernel Documentation](https://learn.microsoft.com/semantic-kernel/)
- [LangChain SQL Documentation](https://python.langchain.com/docs/integrations/toolkits/sql_database)
- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/cognitive-services/openai/)
- [Northwind Database](https://docs.microsoft.com/sql/samples/northwind)