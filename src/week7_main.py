from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel


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

# FastAPI setup
app = FastAPI()
class QuestionRequest(BaseModel):
    question: str



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



#FastAPI route
@app.post("/ask")
def ask_question(input_data: QuestionRequest):
    session_id = str(datetime.now())
    input_state = {"question": input_data.question, "generation": "", "intent": '', "sql_query": '',"faq_keywords":'',"session_id": session_id}

    result = graph.invoke(input_state )
    return {"answer":  result["generation"], "intent":  result["intent"]}


### visit http://127.0.0.1:8000/docs
