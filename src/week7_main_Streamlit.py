import streamlit as st
import pandas as pd
st.set_page_config(page_title="BlueHorizon QA", layout="centered")  # ✅ MUST be first Streamlit command

from dotenv import load_dotenv
from sqlalchemy import create_engine
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

from week7_sql import NL2SQLAgent
from week7_faq import search_service1
#from week6_agents import retrieval_grader
from week7_Supervisoragent import SupervisorAgent_ 
#from week5_chatagent import chat_agent1
from datetime import datetime

import os
#from langchain.callbacks.tracers.langchain import LangChainTracer
#from langchain.callbacks import get_openai_callback
import time
# Load env
load_dotenv()
#tracer = LangChainTracer(project_name="BlueHorizon")



# Define your GraphState
class GraphState(TypedDict):
    question: str
    generation: str
    intent: str
    sql_query:str
    faq_keywords:str
    #history: list[dict[str, str]]  # Add this for chat memory
    session_id: str                # unique user session

# LangGraph Nodes
def SupervisorAgent(state: GraphState) -> GraphState:
    question = state["question"]
    session_id = state["session_id"]
    Supervisor_Agent = SupervisorAgent_()
    result = Supervisor_Agent.generate_response(session_id, {"question": question} ) #, config={"callbacks": [tracer]})
    score = result.intent.lower()
    return {"question": question, "generation": result.message, "intent": score, "sql_query": result.sql_query if  result.intent == "sql_query" else "", "faq_keywords":result.faq_key if  result.intent == "faq" else "" }


NEON_DB_URL = os.getenv("NEON_DB_URL")
engine = create_engine(NEON_DB_URL)
agent = NL2SQLAgent(engine)

def searchsql(state: GraphState) -> Dict[str, Any]:
    question = state["question"]
    SQL_QUERY =state["sql_query"]
    generation = agent.handle_query(question)
    print("🔍 SQL Agent Result:", generation)
    #updated_history = state.get("history", []) + [{"role": "user", "content": question}, {"role": "assistant", "content": generation}]
    return {"question": question, "generation": generation }

def faqagent_(state: GraphState) -> Dict[str, Any]:
    question = state["question"]
    keywords =state["faq_keywords"]
    generation = search_service1(question)
    #updated_history = state.get("history", []) + [{"role": "user", "content": question}, {"role": "assistant", "content": generation}]
    return {"question": question, "generation": generation }







# Graph Construction
FAQAGENT = "faq agent"
SQLAGENT = "sql agent"
SUPERVISORAGENT = "Supervisor Agent"


builder = StateGraph(GraphState)
builder.add_node(SUPERVISORAGENT, SupervisorAgent)
builder.add_node(FAQAGENT, faqagent_)
builder.add_node(SQLAGENT, searchsql)
builder.set_entry_point(SUPERVISORAGENT)


def route_logic(state: GraphState):
    INTENT= state["intent"].lower()
    if   INTENT == "sql_query": return SQLAGENT
    elif INTENT =="faq":        return FAQAGENT
    else:                       return END


builder.add_conditional_edges(SUPERVISORAGENT, route_logic)
builder.add_edge(SQLAGENT, END)
builder.add_edge(FAQAGENT, END)


graph = builder.compile()

# Streamlit UI
st.title("💡 BlueHorizon Question Answering")
question = st.text_input("Ask a question about hotel services:")

if st.button("Submit") and question.strip():
  if "session_id" not in st.session_state: st.session_state.session_id = str(datetime.now())
  #chat_agent_instance = chat_agent1()  # call the function
  #previous_memory = chat_agent_instance.get_memory(st.session_state.session_id)
  #history_list = []
  #for item in previous_memory:
  #  if item.startswith("User:"):
  #      history_list.append({"role": "user", "content": item[6:].strip()})
  #  elif item.startswith("AI:"):
  #      history_list.append({"role": "assistant", "content": item[4:].strip()})
  
  input_state = {"question": question, "generation": "", "intent": '', "sql_query": '',"faq_keywords":'',"session_id": st.session_state.session_id}
  
  
  with st.spinner("Thinking..."):
        start_time = time.time()
        #with get_openai_callback() as cb:
        result = graph.invoke(input_state )#, config={"callbacks": [tracer]})
        latency = round(time.time() - start_time, 2)
        #total_tokens = cb.total_tokens
        #total_cost = cb.total_cost

  st.success("Answer:")
    #st.write(result["generation"])
  generation = result["generation"]
  intent_ = result["intent"]

  st.markdown(f"🔍 Intent: **{intent_}**")
  
  st.markdown("### 📊 LangSmith Execution Metrics")
  st.metric("⏱️ Latency", f"{latency} seconds")
  #st.metric("📄 Tokens Used", f"{total_tokens}")
  #st.metric("💰 Cost (USD)", f"${total_cost:.4f}")

# -------------------------------
# Case 1: SQL Agent (structured data)
# -------------------------------

  if intent_== 'sql_query':
    st.markdown("### 🏨 Available Rooms")
    
    if isinstance(generation, list):
        try:
            # Show details as formatted list
            for room in generation:
                if isinstance(room, (tuple, list)):
                   st.markdown(
                        f"""
                        - **Room ID**: `{room[0]}`
                        - **Room Type**: `{room[3]}`
                        - **View**: `{room[9]}`
                        - **Bed Type**: `{room[8]}`
                        - **Status**: `{room[11]}`
                        - **Base Rate**: `${room[13]}`  
                        - **Max Rate**: `${room[14]}`
                        ---
                        """
                    )
                else:
                    st.markdown(f"- {room}")

            # Optional: Display as table
            with st.expander("📊 View as Table"):
                columns = [
                    "room_id", "room_number", "floor", "type", "square_feet",
                    "basic_amenities", "additional_amenities", "max_occupancy",
                    "bed_type", "view_type", "accessibility", "status",
                    "last_renovation", "base_rate", "max_rate"
                ]
                st.write("🔍 Sample row:", generation[0])
                st.write("🧮 Row length:", len(generation[0]))
                df = pd.DataFrame(generation, columns=columns)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", csv, "rooms.csv", "text/csv")
                st.dataframe(df)

        except Exception as e:
            st.error("⚠️ Could not display structured SQL results.")
            st.write(generation)
            st.write(e)
    else:
        st.warning("Expected structured SQL results, got:")
        st.write(generation)

# -------------------------------
# Case 2: FAQ Agent (natural language answer)
# -------------------------------
  elif intent_== 'faq':
    st.markdown("### 💬 Hotel FAQ Response")
    if generation:
        st.success(generation)
    else:
        st.info("No answer found.")
  else:
    st.markdown("### 💬 Chat Response")
    if generation:
        st.success(generation)
    else:
        st.info("No answer found.") 
      
    
