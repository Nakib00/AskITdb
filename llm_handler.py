# llm_handler.py
import sqlite3
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
import re

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def get_db_schema(db_path: str) -> str:
    """
    Reads the schema of an SQLite database and returns it as a formatted string
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            
            schema_description = "# Database Schema\n\n"
            
            for table in tables:
                schema_description += f"## Table: `{table}`\n"
                
                # Get columns
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                
                schema_description += "| Column Name | Type | Nullable | Primary Key |\n"
                schema_description += "|-------------|------|----------|-------------|\n"
                
                for col in columns:
                    col_id, col_name, col_type, nullable, default_val, pk = col
                    schema_description += f"| `{col_name}` | `{col_type}` | {'✅' if nullable else '❌'} | {'🔑' if pk else ''} |\n"
                
                # Add row count estimate
                cursor.execute(f"SELECT COUNT(*) FROM {table} LIMIT 1;")
                has_data = " (contains data)" if cursor.fetchone()[0] > 0 else ""
                schema_description += f"\n*Row count: ~{cursor.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]:,}*{has_data}\n\n"
            
            return schema_description
    except sqlite3.Error as e:
        return f"# Database Schema\n\nError reading schema: {str(e)}"

def clean_sql_query(raw_query: str) -> str:
    """
    Cleans and formats the SQL query from LLM output
    """
    # Remove markdown code block formatting
    clean_query = re.sub(r'```sql|```', '', raw_query, flags=re.IGNORECASE).strip()
    
    # Remove any text before the first SELECT (if present)
    if 'SELECT' in clean_query.upper():
        clean_query = clean_query[clean_query.upper().find('SELECT'):]
    
    # Ensure the query ends with a semicolon
    if not clean_query.endswith(';'):
        clean_query += ';'
    
    # Remove any trailing text after semicolon
    if ';' in clean_query:
        clean_query = clean_query[:clean_query.find(';')+1]
    
    return clean_query

def get_sql_query(user_query: str, db_schema: str) -> str:
    """
    Converts a natural language question into an SQL query using the DB schema
    """
    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an expert SQL developer. Convert the user's question into a precise SQLite query.
        Use ONLY the following database schema:

        {db_schema}

        Question: {user_query}

        Important Rules:
        1. Return ONLY the SQL query - no explanations, no markdown formatting
        2. Use standard SQLite syntax
        3. Always qualify column names with table names when joining tables
        4. Add LIMIT 100 for queries that might return many rows
        5. Use aggregate functions (COUNT, SUM, AVG) when appropriate
        6. Format dates using SQLite date functions if needed
        7. Handle NULL values appropriately with COALESCE or IS NULL checks
        
        Example response:
        SELECT column1, column2 FROM table WHERE condition LIMIT 100;
        """
    )

    llm = ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name="llama3-70b-8192",
        temperature=0.1
    )

    # Create and execute the chain
    chain = prompt_template | llm | StrOutputParser()
    raw_query = chain.invoke({"user_query": user_query, "db_schema": db_schema})
    
    # Clean and return the query
    return clean_sql_query(raw_query)