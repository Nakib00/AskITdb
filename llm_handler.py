# llm_handler.py

import os
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

def get_sql_query(user_query: str) -> str:
    """
    Converts a natural language question into an SQL query using a language model.

    Args:
        user_query: The user's question in English.

    Returns:
        A valid SQL query string.
    """
    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an expert in converting English questions to SQL query!
        The SQL database has the name STUDENT and has the following columns - NAME, COURSE,
        SECTION and MARKS.

        For example:
        - "How many entries of records are present?" should become "SELECT COUNT(*) FROM STUDENT;"
        - "Tell me all the students studying in Data Science COURSE?" should become "SELECT * FROM STUDENT where COURSE='Data Science';"

        Important: The final SQL code should not have "```" at the beginning or end, and should not include the word "sql".
        
        Now, convert the following question into a valid SQL query: {user_query}
        No preamble, only valid SQL please.
        """
    )

    model = "llama3-8b-8192"
    llm = ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name=model
    )

    # Create the chain and invoke it
    chain = prompt_template | llm | StrOutputParser()
    response = chain.invoke({"user_query": user_query})
    
    return response