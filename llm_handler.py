# llm_handler.py

import os
import sqlite3
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_schema(db_path: str) -> str:
    """
    Reads the schema of an SQLite database and returns it as a formatted string.

    Args:
        db_path: The file path to the SQLite database.

    Returns:
        A string describing the database schema.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            schema_description = "Database schema:\n"
            for table_name in tables:
                table_name = table_name[0]
                schema_description += f"Table '{table_name}':\n"
                # Get column information for each table
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                for column in columns:
                    # column format: (id, name, type, notnull, default_value, pk)
                    col_name = column[1]
                    col_type = column[2]
                    schema_description += f"  - {col_name} ({col_type})\n"
            return schema_description
    except sqlite3.Error as e:
        return f"Error reading database schema: {e}"

def get_sql_query(user_query: str, db_schema: str) -> str:
    """
    Converts a natural language question into an SQL query using the DB schema.

    Args:
        user_query: The user's question in English.
        db_schema: The schema of the database to be queried.

    Returns:
        A valid SQL query string.
    """
    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an expert in converting English questions to SQL queries!
        Based on the database schema below, write a SQL query that answers the user's question.

        {db_schema}

        Question: {user_query}

        Important Rules:
        - The final SQL query should not have "```" at the beginning or end.
        - Do not include the word "sql" in the output.
        - Provide only a valid SQL query. No preamble or explanation.
        """
    )

    model = "llama3-8b-8192"
    llm = ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name=model
    )

    # Create the chain and invoke it
    chain = prompt_template | llm | StrOutputParser()
    response = chain.invoke({"user_query": user_query, "db_schema": db_schema})
    
    return response