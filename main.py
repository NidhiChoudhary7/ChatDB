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

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = openai_key


def main():
    print("\n===== Welcome to the Interactive NL2SQL Database Query System =====")
    print("Ask questions about your database in natural language.")
    print("Type 'exit', 'quit', or 'q' to end the session.\n")
    
    try:
        # Initialize components
        print("Initializing database connection...")
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
        
        print("System ready! You can start asking questions.\n")
        
        # Interactive loop for questions
        while True:
            # Get question from user
            question = input("\n📝 Your question: ")
            
            # Check if user wants to exit
            if question.lower() in ["exit", "quit", "q"]:
                print("\nThank you for using the NL2SQL system. Goodbye!")
                break
            
            # Skip empty questions
            if not question.strip():
                continue
                
            print("⏳ Processing your question...")
            
            try:
                # Prepare input with table info and history
                query_input = {
                    "question": question,
                    "table_info": db.get_table_info(),
                    "top_k": 3,
                    "messages": history.messages,
                }
                
                # Get response from the chain
                response = chain.invoke(query_input)
                
                # Update history
                history.add_user_message(question)
                history.add_ai_message(response)
                
                # Print response
                print("\n🤖 Answer:", response)
                
                # Show option for follow-up questions
                print("\nYou can ask a follow-up question or type 'exit' to quit.")
                
            except Exception as e:
                print(f"\n❌ Error processing your question: {str(e)}")
                print("Please try a different question.")
    
    except Exception as e:
        print(f"\n❌ Error initializing the system: {str(e)}")
        print("Please check your environment setup and try again.")


if __name__ == "__main__":
    main()
