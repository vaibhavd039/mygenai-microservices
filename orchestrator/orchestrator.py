import uvicorn
import requests
import os
from fastapi import FastAPI, HTTPException
from typing import TypedDict
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import logging
import google.cloud.logging

load_dotenv()
load_dotenv("../.env")
# Initialize the GCP Logging Client

client = google.cloud.logging.Client()

# Connects standard Python logging to Google Cloud

client.setup_logging()

app = FastAPI()
RESEARCHER_URL = os.getenv("RESEARCHER_URL")
WRITER_URL = os.getenv("WRITER_URL")

class GraphState(TypedDict, total=False):
    topic: str
    research_notes: str
    draft: str

def call_researcher(state: GraphState):
    logging.info("--- Calling Researcher (8001) ---")
    response = requests.post(f"{RESEARCHER_URL}/research", json=state)
    if response.status_code != 200:
        logging.error(f"Researcher Error: {response.text}")
        raise Exception(f"Researcher Error: {response.text}")
    return response.json()

def call_writer(state: GraphState):
    logging.info("--- Calling Writer (8002) ---")
    response = requests.post(f"{WRITER_URL}/write", json=state)
    if response.status_code != 200:
        logging.error(f"Writer Error: {response.text}")
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
    port = int(os.environ.get("PORT", 8000))
    logging.info("Orchestrator Service is starting up..")
    uvicorn.run(app, host="0.0.0.0", port=port)