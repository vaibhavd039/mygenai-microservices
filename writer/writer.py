import uvicorn
import os
from fastapi import FastAPI, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Look for .env in the current folder OR one level up
load_dotenv() 
load_dotenv("../.env") 

app = FastAPI()

# Validate API Key exists before starting
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GOOGLE_API_KEY not found in environment!")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)

@app.post("/write")
async def write_task(state: dict):
    try:
        notes = state.get("research_notes", "No research found.")
        prompt = f"Write a 1-sentence catchy headline for this research: {notes}"
        
        response = llm.invoke(prompt)
        state["draft"] = response.content
        print("SUCCESS: Writer generated content.")
        return state
    except Exception as e:
        print(f"ERROR in Writer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)