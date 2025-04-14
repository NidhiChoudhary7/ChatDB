import pandas as pd
from langchain.chains.openai_tools import create_extraction_chain_pydantic
from pydantic.v1 import BaseModel, Field  # For Pydantic v1 compatibility
from typing import List

class Table(BaseModel):
    """Table in SQL database."""
    name: str = Field(description="Name of table in SQL database.")

def get_table_details():
    """Read the CSV file and return formatted table descriptions"""
    # Read the CSV file into a DataFrame
    table_description = pd.read_csv("vegetable_tables_description.csv")
    
    # Format the table details as a string
    table_details = ""
    for index, row in table_description.iterrows():
        table_details = table_details + "Table Name:" + row['Table'] + "\n" + "Table Description:" + row['Description'] + "\n\n"

    return table_details

def select_relevant_tables(llm, question):
    """Identify which tables are relevant to the user's question"""
    table_details = get_table_details()
    
    table_details_prompt = f"""Return the names of ALL the SQL tables that MIGHT be relevant to the user question. \
    The tables are:

    {table_details}

    Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed."""

    table_chain = create_extraction_chain_pydantic(Table, llm, system_message=table_details_prompt)
    tables = table_chain.invoke({"input": question})
    return [table.name for table in tables]
