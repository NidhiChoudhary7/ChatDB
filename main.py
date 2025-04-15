# main.py - Refactored version
import os
from operator import itemgetter
from langchain.chains import create_sql_query_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Import custom modules
from langchain_utils import get_database_connection, get_llm, get_query_tool
from table_details import select_relevant_tables, get_table_details
from prompts import create_few_shot_prompt, create_sql_generation_prompt, create_answer_prompt
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env", override=True)
openai_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = openai_key

class ChatDBEngine:
    def __init__(self):
        # Initialize components
        self.db = get_database_connection()
        self.llm = get_llm()
        self.execute_query = get_query_tool(self.db)
        
        # Create prompt templates
        few_shot_prompt = create_few_shot_prompt()
        sql_generation_prompt = create_sql_generation_prompt(few_shot_prompt)
        self.answer_prompt = create_answer_prompt()
        
        # Initialize chat history
        self.history = ChatMessageHistory()
        
        # Create SQL query generation chain
        self.generate_query = create_sql_query_chain(self.llm, self.db, sql_generation_prompt)
        
        # Create response generation chain
        self.rephrase_answer = self.answer_prompt | self.llm | StrOutputParser()
        
        # Create a modified chain structure that allows capturing intermediate results
        self.chain = (
            RunnablePassthrough.assign(
                table_names_to_use=lambda x: select_relevant_tables(self.llm, x["question"])
            ) |
            RunnablePassthrough.assign(
                query=self.generate_query
            ).assign(
                result=lambda x: self.execute_query.invoke(x["query"])
            ) |
            self.rephrase_answer
        )
    
    def process_question(self, question):
        try:
            # Prepare input with table info and history
            query_input = {
                "question": question,
                "table_info": self.db.get_table_info(),
                "top_k": 3,
                "messages": self.history.messages,
            }
            
            # First, generate the query (capture it separately)
            query = self.generate_query.invoke(query_input)
            
            # Execute the query
            try:
                result = self.execute_query.invoke(query)
            except Exception as e:
                result = f"Error executing query: {str(e)}"
            
            # Generate the natural language response
            nl_response = self.rephrase_answer.invoke({
                "question": question,
                "query": query,
                "result": result
            })
            
            # Update history
            self.history.add_user_message(question)
            self.history.add_ai_message(nl_response)
            
            # Return all components
            return {
                "status": "success", 
                "response": nl_response,
                "query": query,
                "result": result
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def clear_history(self):
        self.history = ChatMessageHistory()
        return {"status": "success", "message": "Conversation history cleared"}

# Command-line interface function (keep for backward compatibility)
def run_cli():
    print("\n===== Welcome to the Interactive NL2SQL Database Query System =====")
    print("Ask questions about your database in natural language.")
    print("Type 'exit', 'quit', or 'q' to end the session.\n")
    
    try:
        engine = ChatDBEngine()
        print("System ready! You can start asking questions.\n")
        
        while True:
            question = input("\n📝 Your question: ")
            
            if question.lower() in ["exit", "quit", "q"]:
                print("\nThank you for using the NL2SQL system. Goodbye!")
                break
                
            if not question.strip():
                continue
                
            print("⏳ Processing your question...")
            result = engine.process_question(question)
            
            if result["status"] == "success":
                print("\n🤖 Answer:", result["response"])
                print("\nYou can ask a follow-up question or type 'exit' to quit.")
            else:
                print(f"\n❌ Error processing your question: {result['message']}")
                print("Please try a different question.")
                
    except Exception as e:
        print(f"\n❌ Error initializing the system: {str(e)}")
        print("Please check your environment setup and try again.")

if __name__ == "__main__":
    run_cli()
