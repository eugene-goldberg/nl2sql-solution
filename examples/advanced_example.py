"""
Advanced example demonstrating the NL2SQL plugin in a more complex Semantic Kernel scenario.

This example shows how to:
1. Use the NL2SQL plugin within a broader Semantic Kernel agent context
2. Chain natural language queries with other operations
3. Handle errors and provide feedback to the user
"""

import os
import asyncio
import logging
from typing import Dict, Any

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.prompt_template.kernel_prompt_template import KernelPromptTemplate
from semantic_kernel.functions import kernel_function, KernelFunction

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

class DataAnalysisPlugin:
    """
    A simple plugin for analyzing data in natural language.
    This plugin demonstrates how to use the NL2SQL plugin together with other Semantic Kernel capabilities.
    """
    
    def __init__(self, kernel: sk.Kernel):
        """Initialize the DataAnalysisPlugin."""
        self.kernel = kernel
    
    @kernel_function(
        description="Analyze data from a database using natural language",
        name="analyze_data"
    )
    async def analyze_data(self, analysis_request: str) -> str:
        """
        Analyze data by translating the request to SQL and interpreting the results.
        
        Args:
            analysis_request: A natural language request for data analysis
            
        Returns:
            Analysis results as a string
        """
        # Step 1: Get the database query from the analysis request
        nl2sql_function = self.kernel.plugins["NL2SQL"]["query_database"]
        
        try:
            # Execute the natural language query
            query_result = await self.kernel.invoke(nl2sql_function, analysis_request)
            
            # Step 2: If we have results, interpret them
            if query_result and "error" not in query_result.lower():
                interpretation = await self._interpret_results(analysis_request, query_result)
                return f"Analysis Results:\n\n{interpretation}"
            else:
                return f"Unable to retrieve data for analysis. Details: {query_result}"
        except Exception as e:
            logger.error(f"Error in analyze_data: {str(e)}")
            return f"Error analyzing data: {str(e)}"
    
    async def _interpret_results(self, original_request: str, query_results: str) -> str:
        """
        Interpret the query results using a Semantic Kernel prompt.
        
        Args:
            original_request: The original analysis request
            query_results: The results from the SQL query
            
        Returns:
            An interpretation of the results
        """
        # Define a prompt for result interpretation
        interpret_prompt = """
        You are a data analyst assistant. Interpret the following database query results 
        in the context of the original analysis request. Provide insights, trends, and 
        recommendations based on the data.
        
        Original Request: {{$request}}
        
        Query Results:
        {{$results}}
        
        Interpretation:
        """
        
        # Create a prompt template
        prompt_template = KernelPromptTemplate(interpret_prompt)
        prompt_config = sk.PromptTemplateConfig(template=interpret_prompt)
        prompt_template = kernel.create_function_from_prompt(
            prompt_config,
            plugin_name="DataAnalysis",
            function_name="InterpretResults"
        )
        
        # Execute the prompt
        context_variables = sk.ContextVariables()
        context_variables["request"] = original_request
        context_variables["results"] = query_results
        
        interpretation = await self.kernel.invoke(prompt_template, context_variables)
        return str(interpretation)

async def main():
    """Run the advanced example."""
    # Load environment variables
    load_dotenv()
    env_vars = load_environment_variables()
    
    # Initialize the Semantic Kernel
    global kernel
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
        read_only=env_vars["read_only"]  # Use read-only setting from environment
    )
    
    # Register the data analysis plugin
    data_analysis_plugin = DataAnalysisPlugin(kernel)
    kernel.add_plugin(data_analysis_plugin, "DataAnalysis")
    
    # Example complex analysis requests
    analysis_requests = [
        "Analyze sales trends over the last quarter and identify top-performing products",
        "Investigate customer churn patterns and suggest retention strategies",
        "Evaluate employee performance across departments and identify areas for improvement"
    ]
    
    # Process each analysis request
    for request in analysis_requests:
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

if __name__ == "__main__":
    asyncio.run(main())