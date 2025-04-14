from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate, PromptTemplate
from examples import SQL_EXAMPLES

def create_few_shot_prompt():
    """Create a few-shot prompt template using the SQL examples"""
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}\nAzureSQLQuery:"),
            ("ai", "{query}"),
        ]
    )
    
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=SQL_EXAMPLES,
        input_variables=["input"],
    )
    
    return few_shot_prompt

def create_sql_generation_prompt(few_shot_prompt):
    """Create the final prompt template for Azure SQL generation"""
    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an Azure SQL Server expert using SQL Server (T-SQL). Given an input question, create a syntactically correct SQL query to run. Unless otherwise specified.\n\nHere is the relevant table info: {table_info}\nTop K: {top_k}\n\nBelow are examples of questions and their corresponding SQL queries."),
            few_shot_prompt,
            MessagesPlaceholder(variable_name="messages"),
            ("human", "{input}"),
        ]
    )
    
    return final_prompt


def create_answer_prompt():
    """Create a prompt template for rephrasing Azure SQL results into natural language"""
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question in a natural, helpful way.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
    )
    
    return answer_prompt






