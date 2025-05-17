"""
Simple example demonstrating how to use the NL2SQL plugin with Semantic Kernel.

This example shows how to:
1. Initialize the Semantic Kernel
2. Register the NL2SQL plugin
3. Execute natural language queries against a database
"""

import os
import asyncio
import logging

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from dotenv import load_dotenv
import sys
import os

# Add the parent directory to sys.path to import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nl2sql_plugin import register_nl2sql_plugin
from src.utils import load_environment_variables

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Run the example."""
    # Load environment variables from the config directory
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env')
    load_dotenv(config_path)
    env_vars = load_environment_variables()
    
    # Initialize the Semantic Kernel
    kernel = sk.Kernel()
    
    # Add Azure OpenAI chat service
    kernel.add_service(
        AzureChatCompletion(
            service_id="azure-chat-gpt",
            deployment_name=env_vars["azure_openai_deployment_name"],
            api_key=env_vars["azure_openai_api_key"],
            endpoint=env_vars["azure_openai_endpoint"],
            api_version=env_vars["azure_openai_api_version"]
        )
    )
    
    # Register the NL2SQL plugin
    register_nl2sql_plugin(
        kernel=kernel,
        connection_string=env_vars["connection_string"],
        azure_openai_api_key=env_vars["azure_openai_api_key"],
        azure_openai_endpoint=env_vars["azure_openai_endpoint"],
        azure_openai_api_version=env_vars["azure_openai_api_version"],
        azure_openai_deployment_name=env_vars["azure_openai_deployment_name"],
        included_tables=env_vars["included_tables"],
        read_only=env_vars["read_only"]  # Use read-only setting from environment
    )
    
    # Example natural language queries
    queries = [
        "What are the top 5 customers by order total?",
        "Show me all employees who are in the Sales department",
        "What is the average product price by category?"
    ]
    
    # Execute each query
    for query in queries:
        print(f"\n\nExecuting query: '{query}'")
        print("-" * 50)
        
        try:
            # Get the NL2SQL plugin's query_database function
            query_database_function = kernel.plugins["NL2SQL"]["query_database"]
            
            # Execute the query
            result = await kernel.invoke(query_database_function, **{"query": query})
            
            # Print the result
            print(f"Result:\n{result}")
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            print(f"Error: {str(e)}")
    
    # Get schema information
    print("\n\nGetting schema information:")
    print("-" * 50)
    
    try:
        # Get the NL2SQL plugin's get_schema_info function
        get_schema_info_function = kernel.plugins["NL2SQL"]["get_schema_info"]
        
        # Get the schema information
        schema_info = await kernel.invoke(get_schema_info_function)
        
        # Print the schema information
        print(f"Schema Information:\n{schema_info}")
        
    except Exception as e:
        logger.error(f"Error getting schema information: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())