# main.py
import os
import sqlite3
import streamlit as st
from llm_handler import get_sql_query, get_db_schema
import tempfile
import pandas as pd

def return_sql_response(db_path: str, sql_query: str):
    """
    Executes an SQL query and returns results as a DataFrame
    """
    try:
        with sqlite3.connect(db_path) as conn:
            return pd.read_sql_query(sql_query, conn)
    except sqlite3.OperationalError as e:
        st.error(f"Database Error: {e}")
        return None

def main():
    """
    Main function to run the Streamlit application
    """
    st.set_page_config(page_title="Database Analyst", page_icon=":bar_chart:")
    st.header(":speech_balloon: Talk to Your Database")
    st.caption("Upload any SQLite database and ask questions about your data")

    # Initialize session state
    if "db_path" not in st.session_state:
        st.session_state.db_path = None
    if "schema" not in st.session_state:
        st.session_state.schema = ""
    if "history" not in st.session_state:
        st.session_state.history = []

    # Database upload section
    with st.expander("📁 Upload Database", expanded=True):
        uploaded_file = st.file_uploader(
            "Upload SQLite database (.db)", 
            type="db",
            accept_multiple_files=False,
            key="db_uploader"
        )
        
        if uploaded_file is not None:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
                tmp.write(uploaded_file.getvalue())
                st.session_state.db_path = tmp.name
            
            # Get and store schema
            st.session_state.schema = get_db_schema(st.session_state.db_path)
            
            st.success("Database uploaded successfully!")
            
            # Show schema preview
            with st.expander("View Database Schema"):
                st.code(st.session_state.schema)

    # Question input section
    if st.session_state.db_path:
        with st.form("question_form"):
            user_query = st.text_area(
                "Ask a question about your data:", 
                placeholder="E.g.: Show the 5 most expensive products",
                key="user_query"
            )
            submitted = st.form_submit_button("Submit")
            
            if submitted and user_query:
                with st.spinner("Generating SQL query..."):
                    try:
                        # Generate SQL query
                        sql_query = get_sql_query(user_query, st.session_state.schema)
                        
                        # Execute query
                        results = return_sql_response(st.session_state.db_path, sql_query)
                        
                        # Add to history
                        st.session_state.history.insert(0, {
                            "question": user_query,
                            "sql": sql_query,
                            "results": results
                        })
                    except Exception as e:
                        st.error(f"Error processing your request: {str(e)}")

    # Display results
    if st.session_state.history:
        st.divider()
        st.subheader("Query History")
        
        for idx, entry in enumerate(st.session_state.history):
            with st.expander(f"Q{idx+1}: {entry['question']}", expanded=(idx==0)):
                st.subheader("Generated SQL:")
                st.code(entry["sql"], language="sql")
                
                st.subheader("Results:")
                if not entry["results"].empty:
                    st.dataframe(entry["results"])
                else:
                    st.info("No results found")

if __name__ == '__main__':
    main()