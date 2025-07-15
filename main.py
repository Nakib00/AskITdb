# main.py

import os
import sqlite3
import streamlit as st
from llm_handler import get_db_schema, get_sql_query

# --- Database Interaction ---
def execute_sql_query(sql_query: str, db_path: str):
    """
    Executes an SQL query on the specified database and fetches all results.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            return conn.execute(sql_query).fetchall()
    except sqlite3.OperationalError as e:
        st.error(f"Database Error: {e}")
        return None

# --- Main Streamlit App ---
def main():
    st.set_page_config(page_title="Dynamic DB Query", layout="wide")
    st.title("Ask Your Database 💬")
    st.write("Upload your SQLite database, and I'll answer your questions about it!")

    # --- Session State Initialization ---
    if "db_path" not in st.session_state:
        st.session_state.db_path = None
    if "db_schema" not in st.session_state:
        st.session_state.db_schema = None

    # --- Sidebar for DB Upload ---
    with st.sidebar:
        st.header("1. Upload Database")
        uploaded_file = st.file_uploader(
            "Choose a SQLite file (.db, .sqlite, .sqlite3, .sql)", 
            type=["db", "sqlite", "sqlite3"]
        )

        if uploaded_file is not None:
            # Save the uploaded file to a temporary path
            temp_db_path = os.path.join(".", uploaded_file.name)
            with open(temp_db_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Store path and schema in session state
            st.session_state.db_path = temp_db_path
            st.session_state.db_schema = get_db_schema(temp_db_path)
            st.success("Database uploaded successfully!")

    # --- Main App Body ---
    if st.session_state.db_path:
        st.header("2. View Schema")
        st.text_area("Database Schema", value=st.session_state.db_schema, height=200, disabled=True)
        
        st.header("3. Ask a Question")
        user_query = st.text_input("e.g., 'How many entries are in the customers table?'")

        if st.button("Generate & Execute Query"):
            if user_query:
                with st.spinner("Generating SQL query..."):
                    # 1. Get the SQL query from the LLM
                    sql_query = get_sql_query(user_query, st.session_state.db_schema)
                    st.subheader("🔍 Generated SQL Query:")
                    st.code(sql_query, language="sql")

                with st.spinner("Executing query..."):
                    # 2. Execute the query
                    results = execute_sql_query(sql_query, st.session_state.db_path)

                # 3. Display results
                st.subheader("📝 Query Results:")
                if results is not None:
                    if results:
                        st.table(results)
                    else:
                        st.warning("The query returned no results.")
            else:
                st.warning("Please enter a question.")
    else:
        st.info("Please upload a database file to get started.")

if __name__ == '__main__':
    main()