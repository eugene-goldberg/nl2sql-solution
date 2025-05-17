"""
Semantic Kernel NL2SQL Plugin using LangChain.

This module provides the main plugin integration for Semantic Kernel.
"""

import logging
from typing import Dict, List, Any, Optional

import semantic_kernel as sk
from semantic_kernel.functions import kernel_function, KernelFunction
from semantic_kernel.kernel import Kernel

from .langchain_sql_plugin import LangChainSqlPlugin
from .utils import sanitize_input

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NL2SQLPlugin:
    """
    Semantic Kernel plugin that translates natural language to SQL using LangChain.
    
    This plugin integrates with the Semantic Kernel to provide natural language to SQL capabilities
    via LangChain's SQL agent tooling. It handles configuration, setup, and execution of queries.
    """
    
    def __init__(self,
                 connection_string: Optional[str] = None,
                 azure_openai_api_key: Optional[str] = None,
                 azure_openai_endpoint: Optional[str] = None,
                 azure_openai_api_version: Optional[str] = None,
                 azure_openai_deployment_name: Optional[str] = None,
                 included_tables: Optional[List[str]] = None,
                 read_only: bool = True,
                 include_image_columns: bool = False):
        """
        Initialize the NL2SQL plugin for Semantic Kernel.
        
        Args:
            connection_string: Azure SQL connection string. If None, reads from env vars.
            azure_openai_api_key: Azure OpenAI API key. If None, reads from env vars.
            azure_openai_endpoint: Azure OpenAI endpoint. If None, reads from env vars.
            azure_openai_api_version: Azure OpenAI API version. If None, reads from env vars.
            azure_openai_deployment_name: Azure OpenAI deployment name. If None, reads from env vars.
            included_tables: List of tables to include. If None, reads from env vars or includes all.
            read_only: Whether the database connection should be read-only.
            include_image_columns: Whether to include IMAGE and NTEXT columns in schema (default: False).
        """
        self.langchain_plugin = LangChainSqlPlugin(
            connection_string=connection_string,
            azure_openai_api_key=azure_openai_api_key,
            azure_openai_endpoint=azure_openai_endpoint,
            azure_openai_api_version=azure_openai_api_version,
            azure_openai_deployment_name=azure_openai_deployment_name,
            included_tables=included_tables,
            read_only=read_only,
            include_image_columns=include_image_columns
        )
        logger.info("NL2SQL Plugin initialized")
    
    @kernel_function(
        description="Translates a natural language query into SQL and executes it against an Azure SQL database",
        name="query_database"
    )
    def query_database(self, query: str) -> str:
        """
        Execute a natural language query against the database.
        
        Args:
            query: The natural language query to execute.
            
        Returns:
            The result of the SQL query, formatted as a string.
        """
        try:
            logger.info(f"Executing natural language query: {query}")
            
            # Basic input sanitization
            sanitized_query = sanitize_input(query)
            if sanitized_query != query:
                logger.warning("Query was sanitized before processing")
            
            # Execute the query using the LangChain SQL plugin
            result = self.langchain_plugin.query_database_with_natural_language(sanitized_query)
            
            return result
        except Exception as e:
            error_message = f"Error executing query: {str(e)}"
            logger.error(error_message)
            return error_message
    
    @kernel_function(
        description="Gets information about the database schema that the SQL agent can query",
        name="get_schema_info"
    )
    def get_schema_info(self) -> str:
        """
        Get information about the database schema that the SQL agent can query.
        
        Returns:
            A string describing the database schema (tables and columns).
        """
        try:
            # Access the LangChain SQL database object's table info
            db = self.langchain_plugin.db
            
            # Format the schema information as a string
            schema_info = []
            schema_info.append("Database Schema Information:")
            
            # get_usable_table_names() returns a list, not a dict
            table_names = db.get_usable_table_names()
            
            for table_name in table_names:
                schema_info.append(f"\nTable: {table_name}")
                
                # Get column information
                column_info = db.get_table_info([table_name])
                schema_info.append(column_info)
            
            return "\n".join(schema_info)
        except Exception as e:
            error_message = f"Error retrieving schema information: {str(e)}"
            logger.error(error_message)
            return error_message

def register_nl2sql_plugin(kernel: Kernel, 
                          connection_string: Optional[str] = None,
                          azure_openai_api_key: Optional[str] = None,
                          azure_openai_endpoint: Optional[str] = None,
                          azure_openai_api_version: Optional[str] = None,
                          azure_openai_deployment_name: Optional[str] = None,
                          included_tables: Optional[List[str]] = None,
                          read_only: bool = True,
                          include_image_columns: bool = False) -> None:
    """
    Register the NL2SQL plugin with a Semantic Kernel instance.
    
    Args:
        kernel: The Semantic Kernel instance to register the plugin with.
        connection_string: Azure SQL connection string. If None, reads from env vars.
        azure_openai_api_key: Azure OpenAI API key. If None, reads from env vars.
        azure_openai_endpoint: Azure OpenAI endpoint. If None, reads from env vars.
        azure_openai_api_version: Azure OpenAI API version. If None, reads from env vars.
        azure_openai_deployment_name: Azure OpenAI deployment name. If None, reads from env vars.
        included_tables: List of tables to include. If None, reads from env vars or includes all.
        read_only: Whether the database connection should be read-only.
    """
    plugin = NL2SQLPlugin(
        connection_string=connection_string,
        azure_openai_api_key=azure_openai_api_key,
        azure_openai_endpoint=azure_openai_endpoint,
        azure_openai_api_version=azure_openai_api_version,
        azure_openai_deployment_name=azure_openai_deployment_name,
        included_tables=included_tables,
        read_only=read_only,
        include_image_columns=include_image_columns
    )
    
    kernel.add_plugin(plugin, "NL2SQL")
    logger.info("NL2SQL Plugin registered with Semantic Kernel")