import os
import sqlite3
import streamlit as st
from llm_handler import get_sql_query, get_db_schema

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
    submit = st.button("Enter", key="submit_button")

    if submit and user_query:
        database = "student.db"
        
        #  Get schema first
        db_schema = get_db_schema(database)

        #  Then pass both user query and schema
        sql_query = get_sql_query(user_query, db_schema)

        st.subheader("🔍 Generated SQL Query:")
        st.code(sql_query, language="sql")

        #  Execute SQL query
        retrieved_data = return_sql_response(sql_query)

        if retrieved_data:
            st.subheader("📝 Query Results:")
            for row in retrieved_data:
                st.write(row)
        else:
            st.warning("The query returned no results.")

if __name__ == '__main__':
    main()
