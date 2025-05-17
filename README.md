# NL2SQL Solution using LangChain and Semantic Kernel

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready natural language to SQL (NL2SQL) solution that leverages LangChain's SQL capabilities and integrates them as a plugin for Microsoft Semantic Kernel. Transform natural language queries into SQL with the power of Azure OpenAI.

## 🚀 Features

- **Natural Language to SQL**: Convert plain English questions into SQL queries
- **Semantic Kernel Integration**: Seamlessly works with Microsoft's AI orchestration framework
- **Azure OpenAI Powered**: Uses GPT-3.5-Turbo for intelligent query translation
- **Token Optimization**: Smart handling of model token limits
- **Security First**: Read-only mode, input sanitization, and query auditing
- **Self-Correcting**: Automatically adapts SQL syntax for different databases

## Architecture

The solution uses the following architecture:

1. **Semantic Kernel Plugin**: Acts as the interface between Semantic Kernel and LangChain.
2. **LangChain SQL Agent**: Handles the core NL2SQL conversion and execution using:
   - Azure OpenAI for language understanding and SQL generation
   - SQLAlchemy and pyodbc for database connectivity
   - SQL agent capabilities for query construction and execution

## Features

- Translate natural language queries to T-SQL
- Execute SQL queries against Azure SQL databases
- Restrict access to specific tables for security
- Log generated SQL queries for auditing
- Basic input sanitization to help prevent SQL injection
- Schema introspection to understand database structure

## Security Considerations

The solution implements several security measures:

1. **Least Privilege**: Database connection uses credentials with minimal necessary permissions
2. **Input Sanitization**: Basic sanitization of natural language inputs
3. **Logging**: Logs natural language queries and generated SQL for audit purposes
4. **Schema Restriction**: Can be configured to access only specific tables

## 🏁 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/nl2sql-solution.git
cd nl2sql-solution

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp config/.env.example config/.env
# Edit config/.env with your Azure OpenAI and database credentials

# Run the example
python examples/simple_example.py
```

## 📋 Prerequisites

- Python 3.11 or later
- SQL Server (local Docker or Azure SQL Database)
- Azure OpenAI API access
- ODBC Driver 18 for SQL Server
- Python packages (see requirements.txt)

### Installation

1. Clone this repository
2. Install ODBC Driver for SQL Server:

```bash
# Add Microsoft repository
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" | \
  sudo tee /etc/apt/sources.list.d/mssql-release.list

# Install driver
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp config/.env.example config/.env
# Edit the .env file with your configuration
```

### Configuration

In your `.env` file, configure the following:

```
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-07-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_model_deployment_name

# Azure SQL Database Configuration
AZURE_SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=your-server.database.windows.net;Database=your_database;Uid=your_username;Pwd=your_password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;

# Optional: Specify Tables
INCLUDED_TABLES=table1,table2,table3
```

> **Security Note**: Always use a database user with the minimum required permissions. Ideally, use a read-only account if your application only needs to query data.

## Usage Examples

### Basic Usage

```python
import asyncio
import semantic_kernel as sk
from src.nl2sql_plugin import register_nl2sql_plugin

async def main():
    # Initialize Semantic Kernel
    kernel = sk.Kernel()
    
    # Register the NL2SQL plugin (it will read config from .env)
    register_nl2sql_plugin(kernel)
    
    # Execute a natural language query
    nl2sql_function = kernel.plugins["NL2SQL"]["query_database"]
    result = await kernel.invoke(nl2sql_function, "List all customers in New York")
    
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage

See the examples directory for more advanced usage examples:

- `simple_example.py`: Basic usage of the NL2SQL plugin
- `advanced_example.py`: Integration with other Semantic Kernel capabilities

## Implementation Details

### Key Features Implemented

1. **ODBC to SQLAlchemy Conversion**: Automatic conversion of ODBC connection strings to SQLAlchemy format
2. **Token Limit Management**: Custom database class that filters large binary columns to stay within GPT-3.5-Turbo limits
3. **Self-Correcting SQL Generation**: Agent adapts SQL syntax for SQL Server (e.g., TOP vs LIMIT)
4. **Real-time Schema Introspection**: Dynamic discovery of database structure

### File Structure

- `src/nl2sql_plugin.py` - Main Semantic Kernel plugin
- `src/langchain_sql_plugin.py` - LangChain SQL agent integration
- `src/database.py` - Database connection and schema management
- `src/security.py` - Security validation and audit logging
- `src/utils.py` - Utility functions for sanitization

### Customization

#### Adding Custom Validation

You can extend the `utils.py` file to add more sophisticated input validation or SQL query validation.

#### Supporting Additional Database Dialects

This solution is focused on T-SQL for SQL Server, but LangChain supports other SQL dialects. You can modify the `langchain_sql_plugin.py` file to support other database types.

#### Token Limit Handling

Adjust the `include_image_columns` parameter in `database.py` to control column filtering based on your model's token limits.

## Limitations

- The quality of SQL generation depends on the capabilities of the LLM being used
- Complex queries might not be translated accurately
- Schema understanding is limited to the tables and columns explicitly provided

## License

[MIT License](LICENSE)

## Documentation

- [Getting Started Guide](GETTING_STARTED.md) - Complete setup instructions
- [Implementation Notes](IMPLEMENTATION_NOTES.md) - Technical details and decisions
- [Project Overview](PROJECT_OVERVIEW.md) - High-level summary and achievements

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.