import os
from dotenv import load_dotenv
load_dotenv()
your_openai_api_key= os.getenv("OPENAI_API_KEY")
#import openai
import redis
from datetime import datetime
from openai import OpenAI

#from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.output_parsers import PydanticOutputParser
#from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
#from langchain.schema.output_parser import OutputParserException
#from langchain.output_parsers.openai_functions import create_structured_output_function

#from langchain_core.pydantic_v1 import BaseModel, Field
#from langchain_core.pydantic_v1 import BaseModel, Field

from pydantic import BaseModel, Field
#from langchain_openai import ChatOpenAI
import getpass
import time
import os
os.environ["OPENAI_API_KEY"] = your_openai_api_key

 
# Define output schema using Pydantic v2
class SupervisorOutput(BaseModel):
    """
    Output used to guide the next step in the LangGraph agentic flow.
    """
    intent: str = Field(description="Either 'chat', 'faq', or 'sql_query' ")
    message: str = Field(description="A natural language message responding to the user.")
    sql_query: str = Field(default=None, description="SQL query if the intent is 'sql_query'")
    faq_key: str = Field(default=None, description="Relevant FAQ keywords if intent is 'faq'")

# Manually construct OpenAI function schema from Pydantic model
function_spec = {
    "name": "SupervisorOutput",
    "description": "Classify hotel assistant user intent and return structured response.",
    "parameters": SupervisorOutput.model_json_schema()
}

class SupervisorAgent:
    def __init__(self, redis_client, openai_api_key):
        self.redis = redis_client
        self.client = OpenAI(api_key=openai_api_key)

    def get_memory(self, session_id):
        memory = self.redis.get(session_id)
        if memory:
            return memory.decode().split("||")
        return []

    def update_memory(self, session_id, memory):
        self.redis.set(session_id, "||".join(memory))

    def generate_response(self, session_id, query):
        memory = self.get_memory(session_id)
        memory.append(f"User: {query}")
        prompt = "\n".join(memory)
        #openai_function = create_structured_output_function(SupervisorOutput)
        #parser = JsonOutputFunctionsParser(pydantic_schema=SupervisorOutput)
        #parser = PydanticOutputParser(pydantic_object=SupervisorOutput)

        system = """
You are a reasoning agent for a hotel assistant. Given a customer's query, classify the *intent* of the query and generate a response.

Possible intents:
- 'chat': If the question is conversational and needs only a direct reply.
- 'faq': If the query matches frequently asked questions (e.g., check-in time, cancellation policy).
- 'sql_query': If the query requires querying a database (e.g., availability, pricing).

 Respond using the structured format.
         """
        # Create the prompt template
        messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
        ]
  
        response = self.client.chat.completions.create(
        model="gpt-3.5-turbo",  # Preferably GPT-4 for reasoning
        messages=messages,
        temperature=0.3,
        functions=[function_spec],
        function_call={"name": "SupervisorOutput"}
        )
        #parser = PydanticOutputParser(pydantic_object=SupervisorOutput)

        args = response.choices[0].message.function_call.arguments
        structured_output = SupervisorOutput.parse_raw(args)
        memory.append(f"AI: {structured_output.message}")
        self.update_memory(session_id, memory)
        return structured_output



# Initialize Redis and ChatAgent
#redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

chat_agent = SupervisorAgent(redis_client=redis_client, openai_api_key=your_openai_api_key)



def SupervisorAgent_():
    return SupervisorAgent(redis_client=redis_client, openai_api_key=your_openai_api_key)

import streamlit as st
# Streamlit app for chat interface
def run_chat():
    # Generate or reuse session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(datetime.now())
    session_id = st.session_state.session_id

    st.title("Blue Horizon AI Concierge Chat")

    user_input = st.text_input("Ask me anything:")

    if user_input:
        #try:
            response = chat_agent.generate_response(session_id, user_input)
            st.markdown(f"**Intent**: {response.intent}")
            st.markdown(f"**Response**: {response.message}")
            
            if response.intent == "sql_query":
                st.code(response.sql_query, language="sql")
            elif response.intent == "faq":
                st.code(response.faq_key, language="text")

        #except :
        #    st.error("Rate limit exceeded. Please wait and try again in a few seconds.")
        
        #time.sleep(2)  # Prevent hitting rate limits too quickly

# Run the Streamlit app
if __name__ == "__main__":
    run_chat()



