"""
Security utilities for the NL2SQL solution.

This module provides security-focused utilities for validating and sanitizing
inputs and SQL queries.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityValidator:
    """
    Validator for security concerns in natural language and SQL queries.
    
    This class provides methods to validate and sanitize inputs to help
    prevent security issues like SQL injection.
    """
    
    # Patterns that might indicate potentially harmful SQL
    SUSPICIOUS_SQL_PATTERNS = [
        r';\s*DROP\s+TABLE',
        r';\s*DELETE\s+FROM',
        r';\s*TRUNCATE\s+TABLE',
        r';\s*ALTER\s+TABLE',
        r';\s*UPDATE\s+.*\s*SET',
        r';\s*INSERT\s+INTO',
        r';\s*CREATE\s+',
        r';\s*EXEC\s+',
        r';\s*EXECUTE\s+',
        r'xp_cmdshell',
        r'sp_configure',
        r'--',  # SQL comment (could be used to comment out parts of legitimate queries)
        r'/\*.*\*/'  # Multi-line SQL comment
    ]
    
    # Disallowed operations for read-only applications
    DISALLOWED_SQL_OPERATIONS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'UPDATE', 'INSERT', 'CREATE', 
        'EXEC', 'EXECUTE', 'GRANT', 'REVOKE', 'DENY'
    ]
    
    def __init__(self, read_only: bool = True):
        """
        Initialize the security validator.
        
        Args:
            read_only: If True, disallows write operations in SQL queries.
        """
        self.read_only = read_only
    
    def validate_nl_input(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a natural language input for potential security issues.
        
        Args:
            query: The natural language query to validate.
            
        Returns:
            Tuple of (is_valid, error_message). If is_valid is False,
            error_message describes the issue.
        """
        # Check for suspicious SQL-like patterns in natural language
        # This is a basic check for attempts to inject SQL directly in NL
        for operation in self.DISALLOWED_SQL_OPERATIONS:
            if re.search(rf'\b{operation}\b', query, re.IGNORECASE):
                logger.warning(f"Suspicious SQL operation '{operation}' detected in natural language query")
                return False, f"Query contains suspicious operation: {operation}"
        
        return True, None
    
    def validate_sql_query(self, sql_query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a SQL query for potential security issues.
        
        Args:
            sql_query: The SQL query to validate.
            
        Returns:
            Tuple of (is_valid, error_message). If is_valid is False,
            error_message describes the issue.
        """
        # Check for suspicious patterns
        for pattern in self.SUSPICIOUS_SQL_PATTERNS:
            if re.search(pattern, sql_query, re.IGNORECASE):
                logger.warning(f"Suspicious SQL pattern detected: {pattern}")
                return False, f"Query contains suspicious pattern: {pattern}"
        
        # Check for disallowed operations in read-only mode
        if self.read_only:
            for operation in self.DISALLOWED_SQL_OPERATIONS:
                if re.search(rf'\b{operation}\b', sql_query, re.IGNORECASE):
                    logger.warning(f"Disallowed SQL operation '{operation}' detected in read-only mode")
                    return False, f"Operation not allowed in read-only mode: {operation}"
        
        return True, None
    
    def sanitize_nl_input(self, query: str) -> str:
        """
        Basic sanitization of natural language input.
        
        Args:
            query: The natural language query to sanitize.
            
        Returns:
            Sanitized query.
        """
        # Replace SQL-like keywords with spaces to maintain query structure
        sanitized_query = query
        for operation in self.DISALLOWED_SQL_OPERATIONS:
            pattern = rf'\b{operation}\b'
            sanitized_query = re.sub(pattern, ' ' * len(operation), sanitized_query, flags=re.IGNORECASE)
        
        return sanitized_query
    
    def audit_query(self, nl_query: str, sql_query: str, result_status: str) -> Dict[str, Any]:
        """
        Create an audit record for a query.
        
        Args:
            nl_query: The original natural language query.
            sql_query: The generated SQL query.
            result_status: The status of the query execution.
            
        Returns:
            Audit record as a dictionary.
        """
        return {
            "natural_language_query": nl_query,
            "sql_query": sql_query,
            "status": result_status,
            "read_only_mode": self.read_only
        }