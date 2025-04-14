from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

def get_database_connection():
    """Connect to the database using the provided connection string"""
    return SQLDatabase.from_uri(
        "mssql+pyodbc://nidhi_admin:ChatDB%407@nidhiserver.database.windows.net:1433/data?driver=ODBC+Driver+17+for+SQL+Server"
    )

def get_llm(model="gpt-3.5-turbo", temperature=0):
    """Initialize and return the language model"""
    return ChatOpenAI(model=model, temperature=temperature)

def get_query_tool(db):
    """Create a tool for executing SQL queries against the database"""
    return QuerySQLDataBaseTool(db=db)
