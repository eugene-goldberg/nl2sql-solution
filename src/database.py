"""
Database connection management for the NL2SQL solution.

This module provides utilities for securely connecting to Azure SQL Database
and managing database sessions.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
import re

from sqlalchemy import create_engine, inspect, text, MetaData, Table
from langchain_community.utilities.sql_database import SQLDatabase
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LimitedSQLDatabase(SQLDatabase):
    """
    Custom SQLDatabase that filters out large binary columns to avoid token limits.
    """
    
    def __init__(self, engine, schema=None, metadata=None, ignore_tables=None, 
                 include_tables=None, sample_rows_in_table_info=3, maximum_columns=None,
                 include_image_columns=False):
        super().__init__(engine, schema, metadata, ignore_tables, include_tables,
                        sample_rows_in_table_info, maximum_columns)
        self.include_image_columns = include_image_columns
    
    def get_table_info(self, table_names: Optional[List[str]] = None) -> str:
        """Override to filter out IMAGE and large text columns."""
        if table_names is None:
            table_names = self.get_usable_table_names()
        
        metadata = MetaData()
        tables = []
        
        for table_name in table_names:
            table = Table(table_name, metadata, autoload_with=self._engine)
            
            # Create DDL with filtered columns
            create_table_stmt = []
            create_table_stmt.append(f"CREATE TABLE [{table_name}] (")
            
            column_lines = []
            for column in table.columns:
                column_type = str(column.type)
                
                # Skip IMAGE and large TEXT columns if not included
                if not self.include_image_columns:
                    if 'IMAGE' in column_type.upper() or 'NTEXT' in column_type.upper():
                        continue
                
                line = f"\t[{column.name}] {column_type}"
                
                if column.nullable:
                    line += " NULL"
                else:
                    line += " NOT NULL"
                    
                if column.primary_key:
                    line += " PRIMARY KEY"
                    
                column_lines.append(line)
            
            create_table_stmt.append(",\n".join(column_lines))
            create_table_stmt.append(")")
            
            # Add sample rows (filtering out binary data)
            sample_query = f"SELECT TOP {self._sample_rows_in_table_info} * FROM [{table_name}]"
            sample_rows = []
            
            try:
                with self._engine.connect() as conn:
                    result = conn.execute(text(sample_query))
                    rows = result.fetchall()
                
                if rows:
                    # Get column names
                    columns = list(result.keys())
                    
                    # Filter columns if needed
                    if not self.include_image_columns:
                        filtered_columns = []
                        for i, col in enumerate(columns):
                            col_type = str(table.columns[col].type).upper()
                            if 'IMAGE' not in col_type and 'NTEXT' not in col_type:
                                filtered_columns.append((i, col))
                    else:
                        filtered_columns = [(i, col) for i, col in enumerate(columns)]
                    
                    # Create header
                    header = "\t".join([col for _, col in filtered_columns])
                    sample_rows.append(header)
                    
                    # Add rows with filtered data
                    for row in rows:
                        values = []
                        for i, col in filtered_columns:
                            value = row[i]
                            if value is None:
                                values.append("None")
                            elif isinstance(value, bytes):
                                values.append("<binary data>")
                            else:
                                values.append(str(value))
                        sample_rows.append("\t".join(values))
            
            except Exception as e:
                logger.warning(f"Error getting sample rows for {table_name}: {e}")
            
            table_info = "\n".join(create_table_stmt)
            if sample_rows:
                table_info += "\n\n/*\n"
                table_info += f"{len(sample_rows)-1} rows from {table_name} table:\n"
                table_info += "\n".join(sample_rows)
                table_info += "\n*/"
            
            tables.append(table_info)
        
        return "\n\n".join(tables)


class DatabaseManager:
    """
    Manager for database connections and operations.
    
    This class handles connection pooling, schema inspection,
    and other database-related utilities.
    """
    
    def __init__(self, 
                 connection_string: Optional[str] = None,
                 included_tables: Optional[List[str]] = None,
                 sample_rows_in_table_info: int = 3,
                 include_image_columns: bool = False):
        """
        Initialize the database manager.
        
        Args:
            connection_string: SQLAlchemy connection string for Azure SQL Database.
                If None, reads from environment variables.
            included_tables: List of tables to include in schema info.
                If None, includes all tables.
            sample_rows_in_table_info: Number of sample rows to include in table info.
        """
        # Load environment variables if needed
        load_dotenv()
        
        # Get connection string from env vars if not provided
        self.connection_string = connection_string or os.getenv("AZURE_SQL_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("Database connection string not provided and not found in environment variables")
        
        # Get included tables from env vars if not provided
        if included_tables is None:
            included_tables_str = os.getenv("INCLUDED_TABLES", "")
            self.included_tables = [t.strip() for t in included_tables_str.split(",")] if included_tables_str else None
        else:
            self.included_tables = included_tables
        
        # Store other configuration
        self.sample_rows_in_table_info = sample_rows_in_table_info
        self.include_image_columns = include_image_columns
        
        # Initialize database connection
        self._initialize_db()
    
    def _convert_to_sqlalchemy_url(self, connection_string: str) -> str:
        """Convert ODBC connection string to SQLAlchemy format if needed."""
        if connection_string.startswith("mssql+pyodbc://"):
            # Already in SQLAlchemy format
            return connection_string
        
        # Check if it's an ODBC connection string
        if "Driver=" in connection_string:
            # Parse ODBC connection string components
            parts = {}
            for part in connection_string.split(';'):
                if '=' in part:
                    key, value = part.split('=', 1)
                    parts[key.lower()] = value
            
            server = parts.get('server', 'localhost')
            database = parts.get('database', 'master')
            uid = parts.get('uid', '')
            pwd = parts.get('pwd', '')
            
            # Create SQLAlchemy URL for SQL Server with pyodbc
            # Use the same driver specified in the ODBC string
            driver = parts.get('driver', 'ODBC Driver 18 for SQL Server')
            
            # Build the SQLAlchemy URL
            if uid and pwd:
                # Use SQL Server authentication
                sqlalchemy_url = f"mssql+pyodbc://{uid}:{pwd}@{server}/{database}"
            else:
                # Use Windows authentication (though not applicable for Docker)
                sqlalchemy_url = f"mssql+pyodbc://{server}/{database}"
            
            # Add driver name as a query parameter
            # The driver name should not have curly braces in the URL format
            import urllib.parse
            driver_clean = driver.strip('{}')
            sqlalchemy_url += f"?driver={urllib.parse.quote(driver_clean)}"
            
            # Add TrustServerCertificate if present
            if parts.get('trustservercertificate', '').lower() == 'yes':
                sqlalchemy_url += "&TrustServerCertificate=yes"
            
            logger.info(f"Converted ODBC string to SQLAlchemy: {sqlalchemy_url}")
            return sqlalchemy_url
        
        # If not recognized, return as-is
        return connection_string
    
    def _initialize_db(self):
        """Initialize the database connection and SQLDatabase instance."""
        try:
            # Convert ODBC connection string to SQLAlchemy format if needed
            sql_alchemy_string = self._convert_to_sqlalchemy_url(self.connection_string)
            
            # Create engine first
            engine = create_engine(sql_alchemy_string)
            
            # Create custom SQLDatabase instance that filters out large columns
            self.sql_database = LimitedSQLDatabase(
                engine,
                include_tables=self.included_tables,
                sample_rows_in_table_info=self.sample_rows_in_table_info,
                include_image_columns=self.include_image_columns
            )
            
            logger.info(f"Database connection initialized successfully")
            
            # Store reference to the engine for direct access if needed
            self.engine = self.sql_database._engine
            
            # Log available tables (for debugging)
            tables = self.get_table_names()
            logger.info(f"Available tables: {', '.join(tables)}")
            
        except Exception as e:
            logger.error(f"Error initializing database connection: {str(e)}")
            raise
    
    def get_langchain_db(self) -> SQLDatabase:
        """
        Get the LangChain SQLDatabase instance.
        
        Returns:
            LangChain SQLDatabase instance.
        """
        return self.sql_database
    
    def get_table_names(self) -> List[str]:
        """
        Get a list of all table names in the database (or included tables if specified).
        
        Returns:
            List of table names.
        """
        return list(self.sql_database.get_usable_table_names())
    
    def get_table_info(self, table_name: Optional[str] = None) -> str:
        """
        Get schema information for one or all tables.
        
        Args:
            table_name: The name of the table to get info for.
                If None, returns info for all tables.
                
        Returns:
            Schema information as a string.
        """
        if table_name:
            return self.sql_database.get_table_info(table_name=table_name)
        else:
            all_info = []
            for table in self.get_table_names():
                table_info = self.sql_database.get_table_info(table_name=table)
                all_info.append(f"Table: {table}\n{table_info}\n")
            return "\n".join(all_info)
    
    def execute_query(self, query: str) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Execute a raw SQL query directly.
        
        Note: This method bypasses LangChain and should only be used
        for valid, pre-approved queries after stringent validation.
        
        Args:
            query: The SQL query to execute.
            
        Returns:
            Tuple of (results as list of dictionaries, success flag).
        """
        try:
            # Execute the query
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                
                # Convert result to list of dictionaries
                column_names = result.keys()
                rows = result.fetchall()
                
                # Format results
                results = [dict(zip(column_names, row)) for row in rows]
                
                return results, True
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return [{"error": str(e)}], False