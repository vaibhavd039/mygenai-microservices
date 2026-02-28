import uvicorn
import requests
import os
from fastapi import FastAPI, HTTPException
from typing import TypedDict
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()
load_dotenv("../.env")

app = FastAPI()

class GraphState(TypedDict, total=False):
    topic: str
    research_notes: str
    draft: str

def call_researcher(state: GraphState):
    print("--- Calling Researcher (8001) ---")
    response = requests.post("http://127.0.0.1:8001/research", json=state)
    if response.status_code != 200:
        raise Exception(f"Researcher Error: {response.text}")
    return response.json()

def call_writer(state: GraphState):
    print("--- Calling Writer (8002) ---")
    response = requests.post("http://127.0.0.1:8002/write", json=state)
    if response.status_code != 200:
        raise Exception(f"Writer Error: {response.text}")
    return response.json()

workflow = StateGraph(GraphState)
workflow.add_node("researcher", call_researcher)
workflow.add_node("writer", call_writer)
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)
graph = workflow.compile()

@app.post("/run-agent")
async def run_agent(payload: dict):
    # Safety check for payload
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="Missing 'topic' in request body")
        
    initial_input: GraphState = {"topic": topic}
    
    try:
        final_state = graph.invoke(initial_input)
        return final_state
    except Exception as e:
        print(f"ORCHESTRATOR ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)