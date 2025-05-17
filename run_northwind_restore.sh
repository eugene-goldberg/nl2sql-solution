#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# !!! IMPORTANT: Replace "admin$123!" with the actual SA_PASSWORD you set in your docker-compose.yml !!!
SA_PASSWORD="Kpss1s0k"
SQLCMD_PATH="/opt/mssql-tools18/bin/sqlcmd" # Path to sqlcmd in the container
NORTHWIND_SCRIPT_PATH="/tmp/Northwind_instnwnd.sql" # Path to your Northwind SQL script in the container
DB_NAME="Northwind"

# --- Script Logic ---

echo "Attempting to create database '$DB_NAME' if it does not exist..."
# Connect to master (or default) to create the database
# The -b option causes sqlcmd to exit if an error occurs.
$SQLCMD_PATH -S localhost -U SA -P "$SA_PASSWORD" -C -b \
  -Q "IF DB_ID(N'$DB_NAME') IS NULL BEGIN PRINT N'Creating database $DB_NAME...'; CREATE DATABASE [$DB_NAME]; END ELSE BEGIN PRINT N'Database $DB_NAME already exists.'; END"

echo "Successfully ensured database '$DB_NAME' exists or was created."
echo "Running script '$NORTHWIND_SCRIPT_PATH' in the context of database '$DB_NAME'..."

# Execute the main Northwind script within the context of the Northwind database
# The -b option causes sqlcmd to exit if an error occurs.
$SQLCMD_PATH -S localhost -U SA -P "$SA_PASSWORD" -C -b \
  -d "$DB_NAME" \
  -i "$NORTHWIND_SCRIPT_PATH"

echo "Northwind database script execution completed."
echo "You can now connect to the '$DB_NAME' database."

