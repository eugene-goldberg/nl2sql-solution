"""
Utility functions for the LangChain SQL Plugin.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_environment_variables() -> Dict[str, Any]:
    """
    Load environment variables from .env file and return them as a dictionary.
    
    Returns:
        Dictionary containing environment variables.
    """
    load_dotenv()
    
    # Parse read_only flag from environment
    read_only_str = os.getenv("READ_ONLY", "true").lower()
    read_only = read_only_str != "false"  # Default to True for safety
    
    env_vars = {
        "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "azure_openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
        "azure_openai_deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        "connection_string": os.getenv("AZURE_SQL_CONNECTION_STRING"),
        "included_tables": [t.strip() for t in os.getenv("INCLUDED_TABLES", "").split(",")] if os.getenv("INCLUDED_TABLES") else None,
        "read_only": read_only
    }
    
    # Check for missing required variables
    missing_vars = [k for k, v in env_vars.items() if v is None and k not in ["included_tables", "read_only"]]
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
    
    # Log read-only mode status for security awareness
    if not read_only:
        logger.warning("Database is configured in write mode (READ_ONLY=false). This is not recommended for production.")
    else:
        logger.info("Database is configured in read-only mode (default).")
    
    return env_vars

def sanitize_input(query: str) -> str:
    """
    Basic input sanitization for natural language queries.
    
    Note: This is a very basic sanitization and is not a substitute for
    the security provided by proper database permissions and LangChain's
    validation mechanisms.
    
    Args:
        query: The natural language query to sanitize.
        
    Returns:
        Sanitized query.
    """
    # Remove any SQL-like statements or characters that might be injection attempts
    disallowed_keywords = [
        "DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE", 
        "EXEC", "EXECUTE", "xp_", "sp_"
    ]
    
    # Check for suspicious SQL-like patterns
    sanitized_query = query
    for keyword in disallowed_keywords:
        if keyword in sanitized_query.upper():
            logger.warning(f"Potentially suspicious keyword detected in query: {keyword}")
            # Replace with spaces to maintain query structure
            sanitized_query = sanitized_query.upper().replace(keyword, " " * len(keyword)).lower()
    
    return sanitized_query