"""
Test script for NL2SQL solution showing original questions and database results.
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

# Set up minimal logging
logging.basicConfig(level=logging.WARNING)

async def main():
    """Run test queries and display results clearly."""
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
        read_only=env_vars["read_only"]
    )
    
    # Test queries
    test_queries = [
        "What are the top 5 customers by order total?",
        "Show me all employees who are in the Sales department",
        "What is the average product price by category?"
    ]
    
    # Execute and display results
    query_database_function = kernel.plugins["NL2SQL"]["query_database"]
    
    print("\n" + "="*80)
    print("NL2SQL Solution Test Results")
    print("="*80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 60)
        
        try:
            # Execute the query
            result = await kernel.invoke(query_database_function, **{"query": query})
            
            # Display the result
            print("Result from Database Agent:")
            print(result)
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 60)
    
    print("\n" + "="*80)
    print("Test Complete")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())