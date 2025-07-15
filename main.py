# main.py
import os
import sqlite3
import streamlit as st
from llm_handler import get_sql_query, get_db_schema
import tempfile
import pandas as pd
import uuid

# Create temp directory if not exists
TEMP_DIR = "temp_db_files"
os.makedirs(TEMP_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temp directory and return path"""
    unique_id = str(uuid.uuid4())
    file_path = os.path.join(TEMP_DIR, f"{unique_id}.db")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def return_sql_response(db_path: str, sql_query: str):
    """Execute SQL query and return DataFrame"""
    try:
        with sqlite3.connect(db_path) as conn:
            return pd.read_sql_query(sql_query, conn)
    except sqlite3.OperationalError as e:
        st.error(f"Database Error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
        return None

def clear_session():
    """Reset session state"""
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]

def main():
    """Main application function"""
    st.set_page_config(
        page_title="Database Analyst", 
        page_icon=":bar_chart:",
        layout="wide"
    )
    
    st.title(":speech_balloon: Talk to Your Database")
    st.caption("Upload any SQLite database and ask questions about your data")
    
    # Initialize session state
    if "db_path" not in st.session_state:
        st.session_state.db_path = None
    if "schema" not in st.session_state:
        st.session_state.schema = None
    if "history" not in st.session_state:
        st.session_state.history = []
    
    # Sidebar for database management
    with st.sidebar:
        st.header("Database Management")
        
        # Clear button
        if st.button("Clear Session", use_container_width=True):
            clear_session()
            st.rerun()
        
        # Upload section
        uploaded_file = st.file_uploader(
            "Upload SQLite database", 
            type=["db", "sqlite", "sqlite3"],
            accept_multiple_files=False,
            key="uploader"
        )
        
        # Load database
        if uploaded_file and not st.session_state.db_path:
            with st.spinner("Saving database..."):
                st.session_state.db_path = save_uploaded_file(uploaded_file)
            
            with st.spinner("Extracting schema..."):
                try:
                    st.session_state.schema = get_db_schema(st.session_state.db_path)
                    st.success("Database loaded successfully!")
                    
                    # Show schema preview
                    with st.expander("View Schema Summary"):
                        st.code(st.session_state.schema, language="markdown")
                except Exception as e:
                    st.error(f"Schema extraction failed: {str(e)}")
                    st.session_state.db_path = None

    # Main content area
    if st.session_state.db_path and st.session_state.schema:
        # Question input
        with st.form("query_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                user_query = st.text_area(
                    "Ask a question about your data:", 
                    placeholder="E.g.: Show the 10 most expensive products",
                    label_visibility="collapsed"
                )
            with col2:
                submitted = st.form_submit_button("Ask you Database", type="primary")
        
        if submitted and user_query:
            with st.spinner("Generating SQL query..."):
                try:
                    # Generate SQL query
                    sql_query = get_sql_query(user_query, st.session_state.schema)
                    
                    # Execute query
                    with st.spinner("Executing query..."):
                        results = return_sql_response(st.session_state.db_path, sql_query)
                    
                    # Add to history
                    st.session_state.history.insert(0, {
                        "question": user_query,
                        "sql": sql_query,
                        "results": results
                    })
                except Exception as e:
                    st.error(f"Query failed: {str(e)}")
        
        # Display results
        if st.session_state.history:
            st.divider()
            st.subheader("Query History")
            
            for idx, entry in enumerate(st.session_state.history):
                with st.expander(f"Q{idx+1}: {entry['question']}", expanded=(idx == 0)):
                    # SQL query section
                    with st.container(border=True):
                        st.subheader(":gear: Generated SQL")
                        st.code(entry["sql"], language="sql")
                    
                    # Results section
                    if entry["results"] is not None:
                        if not entry["results"].empty:
                            st.subheader(":bar_chart: Results")
                            st.dataframe(entry["results"], use_container_width=True)
                        else:
                            st.info("The query returned no results")
                    else:
                        st.warning("No results available")
    
    elif not st.session_state.db_path:
        # Welcome screen with instructions
        st.info("👈 Please upload a SQLite database file to get started")
        st.markdown("""
        ### How to use:
        1. Upload a SQLite database file (.db, .sqlite, .sqlite3)
        2. Ask questions about your data in natural language
        3. View generated SQL queries and results
        
        ### Supported Questions:
        - "Show me the top 5 customers by total purchases"
        - "What's the average order value?"
        - "List all products with low stock"
        - "Find orders placed in the last 7 days"
        - "How many users signed up last month?"
        """)

if __name__ == '__main__':
    main()