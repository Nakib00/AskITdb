# main.py

import sqlite3
import streamlit as st
from llm_handler import get_sql_query 

def return_sql_response(sql_query: str):
    """
    Executes an SQL query and fetches all results from the database.
    """
    database = "student.db"
    try:
        with sqlite3.connect(database) as conn:
            return conn.execute(sql_query).fetchall()
    except sqlite3.OperationalError as e:
        st.error(f"Database Error: {e}")
        return None

def main():
    """
    Main function to run the Streamlit application.
    """
    st.set_page_config(page_title="Ask IT DB")
    st.header("Talk to your Database! 💬")

    user_query = st.text_input("Ask a question about the student database:")
    submit = st.button("Enter")

    if submit and user_query:
        # 1. Get the SQL query from the LLM
        sql_query = get_sql_query(user_query)
        
        st.subheader(f"🔍 Generated SQL Query:")
        st.code(sql_query, language="sql")
        
        # 2. Execute the query and get data
        retrieved_data = return_sql_response(sql_query)

        # 3. Display the results
        if retrieved_data:
            st.subheader("📝 Query Results:")
            for row in retrieved_data:
                st.write(row)
        else:
            st.warning("The query returned no results.")

if __name__ == '__main__':
    main()