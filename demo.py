"""
NL2SQL Solution Demo

This script demonstrates the NL2SQL plugin for Semantic Kernel
using LangChain for SQL generation and execution.

Usage:
  python3 demo.py [--mode basic|advanced] [--query "your natural language query"]
"""

import os
import sys
import argparse
import asyncio
import logging

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from src.nl2sql_plugin import register_nl2sql_plugin
from src.utils import load_environment_variables
from examples.advanced_example import DataAnalysisPlugin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_basic_demo(kernel, queries=None):
    """Run the basic NL2SQL demo."""
    if not queries:
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
            result = await kernel.invoke(query_database_function, query)
            
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

async def run_advanced_demo(kernel, queries=None):
    """Run the advanced NL2SQL demo with data analysis."""
    # Register the data analysis plugin
    data_analysis_plugin = DataAnalysisPlugin(kernel)
    kernel.add_plugin(data_analysis_plugin, "DataAnalysis")
    
    if not queries:
        queries = [
            "Analyze sales trends over the last quarter and identify top-performing products",
            "Investigate customer churn patterns and suggest retention strategies",
            "Evaluate employee performance across departments and identify areas for improvement"
        ]
    
    # Process each analysis request
    for request in queries:
        print(f"\n\nProcessing analysis request: '{request}'")
        print("-" * 80)
        
        try:
            # Get the data analysis function
            analyze_data_function = kernel.plugins["DataAnalysis"]["analyze_data"]
            
            # Execute the analysis
            result = await kernel.invoke(analyze_data_function, request)
            
            # Print the result
            print(f"Result:\n{result}")
            
        except Exception as e:
            logger.error(f"Error processing analysis request: {str(e)}")
            print(f"Error: {str(e)}")

async def main():
    """Run the demo."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='NL2SQL Solution Demo')
    parser.add_argument('--mode', choices=['basic', 'advanced'], default='basic',
                      help='Demo mode: basic (simple queries) or advanced (data analysis)')
    parser.add_argument('--query', type=str, help='Natural language query to execute')
    args = parser.parse_args()
    
    # Load environment variables
    env_vars = load_environment_variables()
    
    # Check for required configuration
    missing_vars = [k for k, v in env_vars.items() 
                    if v is None and k not in ["included_tables", "read_only"]]
    if missing_vars:
        print(f"Missing required configuration: {', '.join(missing_vars)}")
        print("Please set these variables in the config/.env file.")
        sys.exit(1)
    
    # Initialize the Semantic Kernel
    kernel = sk.Kernel()
    
    # Add Azure OpenAI chat service
    kernel.add_service(
        AzureChatCompletion(
            service_id="azure-chat-gpt",
            deployment_name=env_vars["azure_openai_deployment_name"],
            endpoint=env_vars["azure_openai_endpoint"],
            api_key=env_vars["azure_openai_api_key"],
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
    
    # Run the appropriate demo
    queries = [args.query] if args.query else None
    
    print(f"\nRunning NL2SQL Solution Demo in {args.mode.upper()} mode")
    print("=" * 80)
    
    if args.mode == 'basic':
        await run_basic_demo(kernel, queries)
    else:
        await run_advanced_demo(kernel, queries)

if __name__ == "__main__":
    asyncio.run(main())