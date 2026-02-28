import uvicorn
from fastapi import FastAPI, HTTPException
import os

app = FastAPI()

@app.post("/research")
async def research_task(state: dict):
    try:
        topic = state.get("topic", "AI")
        # Adding some logic to ensure state is updated correctly
        state["research_notes"] = f"Deep research on {topic}: Microservices allow independent scaling of LLM nodes."
        print(f"SUCCESS: Researcher processed {topic}")
        return state
    except Exception as e:
        print(f"ERROR in Researcher: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)