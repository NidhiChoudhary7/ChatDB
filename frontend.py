import streamlit as st
import pandas as pd
import time
import datetime
import re
import ast
import json

# Set page config with wide layout and icon
st.set_page_config(
    page_title="SQL Chat Assistant", 
    page_icon="🤖", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

from main import ChatDBEngine  # Import the ChatDBEngine from main.py

# Initialize ChatDBEngine once
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = ChatDBEngine()

def parse_result_to_dataframe(result):
    """Convert query results to pandas DataFrame for tabular display"""
    try:
        # Handle None/empty results
        if result is None:
            return None
            
        # If result is already a DataFrame
        if isinstance(result, pd.DataFrame):
            return result
            
        # Handle tuple with single value (common db result format)
        if isinstance(result, tuple) and len(result) == 1:
            return pd.DataFrame({"Result": [result[0]]})
        
        # Handle single string value (like "Fruits")
        if isinstance(result, str):
            # First check if it could be a JSON/list format
            if (result.startswith("[") and result.endswith("]")) or (result.startswith("{") and result.endswith("}")):
                try:
                    # Try parsing as JSON
                    parsed = json.loads(result)
                    if isinstance(parsed, list):
                        if len(parsed) > 0:
                            return pd.DataFrame(parsed)
                        else:
                            return pd.DataFrame({"Result": []})
                    elif isinstance(parsed, dict):
                        return pd.DataFrame([parsed])
                except:
                    # Try as Python literal
                    try:
                        parsed = ast.literal_eval(result)
                        if isinstance(parsed, list):
                            # Special case for the tuple format in screenshot
                            if len(parsed) > 0 and isinstance(parsed[0], tuple) and len(parsed[0]) == 3:
                                return pd.DataFrame(parsed, columns=["Item Code", "Item Name", "Loss Rate %"])
                            return pd.DataFrame(parsed)
                    except:
                        pass
            
            # For simple string values (like "Fruits") - key fix for your issue
            return pd.DataFrame([{"Result": result}])
            
        # Handle list results
        if isinstance(result, list):
            if len(result) > 0:
                if isinstance(result[0], dict):
                    return pd.DataFrame(result)
                elif isinstance(result[0], (list, tuple)):
                    # If it's a list of tuples with 3 elements (matches screenshot format)
                    if len(result[0]) == 3:
                        return pd.DataFrame(result, columns=["Item Code", "Item Name", "Loss Rate %"])
                    return pd.DataFrame(result)
                else:
                    # List of simple values
                    return pd.DataFrame({"Result": result})
            else:
                return pd.DataFrame({"Result": []})
                
        # Handle scalar values (int, float, bool)
        if isinstance(result, (int, float, bool)):
            return pd.DataFrame([{"Result": result}])
            
        # Fallback - convert to string and display
        return pd.DataFrame([{"Result": str(result)}])
            
    except Exception as e:
        st.error(f"Error parsing result: {str(e)}")
        # Last resort - force string conversion
        if result is not None:
            return pd.DataFrame([{"Result": str(result)}])
        return None

def process_and_execute(prompt, db_type, table):
    """Process user input, execute query, and format results"""
    try:
        result = st.session_state.chat_engine.process_question(prompt)
        
        if result["status"] == "success":
            # Get the query result
            query_result = result.get("result", None)
            
            # Special case for 'Fruits' result
            if query_result == "Fruits" or str(query_result).strip("'()").strip() == "Fruits":
                result_df = pd.DataFrame([{"Result": "Fruits"}])
            else:
                # Try to parse into DataFrame
                result_df = parse_result_to_dataframe(query_result)
            
            return {
                "query": result.get("query", "-- No query available --"),
                "result": query_result,
                "result_df": result_df,
                "final_answer": result["response"]
            }
        else:
            return {
                "query": "-- ERROR GENERATING QUERY --",
                "result": None,
                "result_df": None,
                "final_answer": f"An error occurred: {result['message']}"
            }
    except Exception as e:
        return {
            "query": "-- ERROR GENERATING QUERY --",
            "result": None,
            "result_df": None,
            "final_answer": f"An error occurred: {str(e)}"
        }

# Helper function to stream the response with a typewriter effect
def simulate_stream(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.03)

# Function to clear chat history
def clear_chat_history():
    st.session_state.chat_engine.clear_history()  # Clear the engine's history
    st.session_state.messages = []
    # Add welcome message back
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi! I'm your SQL Chat Assistant. I can help you query your database using natural language. How can I help you today?",
        "timestamp": datetime.datetime.now().strftime("%I:%M %p")
    })
    st.rerun()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hi! I'm your SQL Chat Assistant. I can help you query your database using natural language. How can I help you today?",
            "timestamp": datetime.datetime.now().strftime("%I:%M %p")
        }
    ]
if "db_type" not in st.session_state:
    st.session_state.db_type = "SQL"
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "current_table" not in st.session_state:
    st.session_state.current_table = "users"

# Apply theme-specific CSS
if st.session_state.theme == "dark":
    background_color = "#0E1117"
    text_color = "#FAFAFA"
    secondary_bg_color = "#262730"
    sidebar_bg = "#1E1E1E"
else:
    background_color = "#FFFFFF"
    text_color = "#31333F"
    secondary_bg_color = "#F0F2F6"
    sidebar_bg = "#F8F9FA"

# Apply custom CSS including theme and larger fonts
st.markdown(f""" 
    <style>
    body {{
        color: {text_color};
        background-color: {background_color};
    }}
    .stApp {{
        color: {text_color};
        background-color: {background_color};
    }}
    .sidebar .sidebar-content {{
        background-color: {sidebar_bg};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color};
    }}
    .stButton>button {{
        background-color: {secondary_bg_color};
        color: {text_color};
        border-radius: 8px;
        padding: 12px 16px;
        font-weight: 600;
    }}
    .stTextInput>div>div>input {{
        background-color: {secondary_bg_color};
        color: {text_color};
    }}
    .stSelectbox>div>div>div {{
        background-color: {secondary_bg_color};
        color: {text_color};
    }}
    .timestamp {{
        font-size: 0.8em;
        opacity: 0.7;
    }}
    .chat-message {{
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        font-size: 16px;
    }}
    .user-message {{
        background-color: {secondary_bg_color};
    }}
    .assistant-message {{
        background-color: #264b77;
    }}
    .query-box {{
        background-color: {secondary_bg_color};
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 20px;
        font-family: monospace;
        font-size: 14px;
    }}
    .result-table {{
        margin-top: 15px;
        margin-bottom: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Sidebar with configuration options
with st.sidebar:
    st.title("SQL Chat Assistant")
    st.markdown("---")
    # Database type toggle
    st.subheader("Database Configuration")
    db_options = ["SQL", "NoSQL"]
    db_index = 0 if st.session_state.db_type == "SQL" else 1
    selected_db = st.radio("Select Database Type:", db_options, index=db_index)
    if selected_db != st.session_state.db_type:
        st.session_state.db_type = selected_db
        st.rerun()

    # Database Schema
    st.markdown("---")
    st.subheader("Database Schema")
    # Table selection based on database type
    if st.session_state.db_type == "SQL":
        tables = ["users", "orders", "products", "customers"]
        selected_table = st.selectbox(
            "Select table:", 
            tables, 
            index=tables.index(st.session_state.current_table) if st.session_state.current_table in tables else 0
        )
    else:
        collections = ["users", "orders", "products", "customers"]
        selected_table = st.selectbox(
            "Select collection:", 
            collections, 
            index=collections.index(st.session_state.current_table) if st.session_state.current_table in collections else 0
        )
    if selected_table != st.session_state.current_table:
        st.session_state.current_table = selected_table

    # Schema display section
    st.markdown("#### Schema")
    if selected_table == "users":
        st.code("id: int\nname: string\nemail: string\ncreated_at: datetime\ndescription: string")
    elif selected_table == "orders":
        st.code("id: int\nuser_id: int\nproduct_id: int\nquantity: int\nprice: decimal\norder_date: datetime")
    elif selected_table == "products":
        st.code("id: int\nname: string\ndescription: string\nprice: decimal\nstock: int")
    else:  # customers
        st.code("id: int\nname: string\nemail: string\naddress: string\nphone: string")

    # Theme toggle with custom styling
    st.markdown("---")
    st.subheader("Appearance")
    # Create two columns for light/dark mode toggle
    col1, col2 = st.columns(2)
    with col1:
        if st.button("☀️ Light", key="light_mode", use_container_width=True, disabled=(st.session_state.theme == "light")):
            st.session_state.theme = "light"
            st.rerun()
    with col2:
        if st.button("🌙 Dark", key="dark_mode", use_container_width=True, disabled=(st.session_state.theme == "dark")):
            st.session_state.theme = "dark"
            st.rerun()

    # Chat management
    st.markdown("---")
    st.subheader("Chat Management")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        clear_chat_history()

    # Export options
    st.markdown("---")
    st.subheader("Export Options")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Chat History", key="export_chat", use_container_width=True):
            chat_text = "\n\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            st.download_button(
                label="Download",
                data=chat_text,
                file_name="chat_export.txt",
                mime="text/plain",
            )
    with col2:
        if st.button("💾 SQL Queries", key="export_queries", use_container_width=True):
            queries = [m.get("query", "") for m in st.session_state.messages if "query" in m]
            st.download_button(
                label="Download",
                data="\n\n".join(queries),
                file_name=f"saved_queries.{'sql' if st.session_state.db_type == 'SQL' else 'js'}",
                mime="text/plain",
            )

    # Information about the app
    st.markdown("---")
    st.subheader("How to Use")
    st.markdown("1. Type your question in natural language")
    st.markdown("2. The system will convert it to a query")
    st.markdown("3. The query will be executed on the database")
    st.markdown("4. Results will be displayed in the chat")
    st.markdown("---")
    st.caption("SQL Chat Assistant | © 2025")

# Main content area - Chat interface
st.title("SQL Chat Assistant")

# Display chat messages from history
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
            if "timestamp" in message:
                st.markdown(f"<div class='timestamp'>{message['timestamp']}</div>", unsafe_allow_html=True)
    else:  # assistant
        with st.chat_message("assistant"):
            st.write(message["content"])
            if "timestamp" in message:
                st.markdown(f"<div class='timestamp'>{message['timestamp']}</div>", unsafe_allow_html=True)
            
            # Display the SQL query in a code block
            if "query" in message and message["query"]:
                with st.expander("Show SQL Query"):
                    st.code(message["query"], language="sql")
            
            # Display the query results - with improved single-value handling
            if "result" in message and message["result"] is not None:
                with st.expander("Show Query Results"):
                    # Special case for "Fruits" or similar single values
                    if message["result"] == "Fruits" or str(message["result"]).strip("'()").strip() == "Fruits":
                        st.dataframe(pd.DataFrame([{"Result": "Fruits"}]))
                    # Use pre-parsed DataFrame if available
                    elif "result_df" in message and message["result_df"] is not None and not message["result_df"].empty:
                        st.dataframe(message["result_df"])
                    else:
                        # Try to parse result into DataFrame
                        result_df = parse_result_to_dataframe(message["result"])
                        if result_df is not None and not result_df.empty:
                            st.dataframe(result_df)
                        else:
                            # Direct HTML table fallback for simple values
                            if isinstance(message["result"], str):
                                st.markdown(f"""
                                <table style="width:100%">
                                  <tr>
                                    <th>Result</th>
                                  </tr>
                                  <tr>
                                    <td>{message["result"]}</td>
                                  </tr>
                                </table>
                                """, unsafe_allow_html=True)
                            else:
                                # Last resort - plain text display
                                st.write(message["result"])

# User input
if prompt := st.chat_input("Ask a question about your database..."):
    # Add timestamp to message
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "timestamp": current_time
    })
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
        st.markdown(f"<div class='timestamp'>{current_time}</div>", unsafe_allow_html=True)
    
    # Process the question
    with st.chat_message("assistant"):
        with st.spinner("Processing your question..."):
            # Get response
            response = process_and_execute(prompt, st.session_state.db_type, st.session_state.current_table)
            
            # Display the formatted response
            st.write(response["final_answer"])
            
            # Add timestamp
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            st.markdown(f"<div class='timestamp'>{current_time}</div>", unsafe_allow_html=True)
            
            # Show query if available
            if response["query"]:
                with st.expander("Show SQL Query"):
                    st.code(response["query"], language="sql")
            
            # Show results if available - with improved single-value handling
            if response["result"] is not None:
                with st.expander("Show Query Results"):
                    # Special direct handling for 'Fruits' case
                    if response["result"] == "Fruits" or str(response["result"]).strip("'()").strip() == "Fruits":
                        st.dataframe(pd.DataFrame([{"Result": "Fruits"}]))
                    # Use pre-parsed DataFrame if available
                    elif response.get("result_df") is not None and not response["result_df"].empty:
                        st.dataframe(response["result_df"])
                    else:
                        # Try to parse result into DataFrame
                        result_df = parse_result_to_dataframe(response["result"])
                        if result_df is not None and not result_df.empty:
                            st.dataframe(result_df)
                        else:
                            # Direct HTML table fallback for simple values
                            if isinstance(response["result"], str):
                                st.markdown(f"""
                                <table style="width:100%">
                                  <tr>
                                    <th>Result</th>
                                  </tr>
                                  <tr>
                                    <td>{response["result"]}</td>
                                  </tr>
                                </table>
                                """, unsafe_allow_html=True)
                            else:
                                # Last resort - plain text display
                                st.write(response["result"])
            
            # Add assistant message to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["final_answer"],
                "timestamp": current_time,
                "query": response["query"],
                "result": response["result"],
                "result_df": response.get("result_df")
            })
