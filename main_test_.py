import os
from operator import itemgetter
from langchain.chains import create_sql_query_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Import our custom modules
from langchain_utils import get_database_connection, get_llm, get_query_tool
from table_details import select_relevant_tables, get_table_details
from prompts import create_few_shot_prompt, create_sql_generation_prompt, create_answer_prompt
from dotenv import load_dotenv

# Set your OpenAI API key
openai_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = "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"


def main():
    # Initialize components
    db = get_database_connection()
    llm = get_llm()
    execute_query = get_query_tool(db)
    
    # Create prompt templates
    few_shot_prompt = create_few_shot_prompt()
    sql_generation_prompt = create_sql_generation_prompt(few_shot_prompt)
    answer_prompt = create_answer_prompt()
    
    # Initialize chat history
    history = ChatMessageHistory()
    
    # Create SQL query generation chain
    generate_query = create_sql_query_chain(llm, db, sql_generation_prompt)
    
    # Create response generation chain
    rephrase_answer = answer_prompt | llm | StrOutputParser()
    
    # Create the complete chain
    chain = (
        RunnablePassthrough.assign(
            table_names_to_use=lambda x: select_relevant_tables(llm, x["question"])
        ) |
        RunnablePassthrough.assign(
            query=generate_query
        ).assign(
            result=itemgetter("query") | execute_query
        ) |
        rephrase_answer
    )
    
    # Example usage
    question = "which item has the highest loss percentage?"
    query_input = {
    "question": question,
    "table_info": db.get_table_info(),  
    "top_k": 3,  
    "messages": history.messages,
}
    response = chain.invoke(query_input)
    
    # Update history
    history.add_user_message(question)
    history.add_ai_message(response)
    
    print("Question:", question)
    print("Response:", response)
    
    # Follow-up question example
    follow_up = "what is it's category"
    follow_up_response = chain.invoke({"question": follow_up, "messages": history.messages})
    
    print("\nFollow-up:", follow_up)
    print("Response:", follow_up_response)

if __name__ == "__main__":
    main()
