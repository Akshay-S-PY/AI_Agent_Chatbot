# backend.py
# -------------------------
# FastAPI app that validates input and calls the agent helper.

from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

from ai_agent import get_response_from_ai_agent, ALLOWED_MODEL_NAMES, ALLOWED_PROVIDERS


# ---------- Schemas ----------
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class RequestState(BaseModel):
    model_name: str
    model_provider: Literal["Groq", "OpenAI", "Anthropic", "Ollama"]
    system_prompt: str
    messages: List[ChatMessage]  # proper structured messages
    allow_search: bool = False


# ---------- App ----------
app = FastAPI(title="LangGraph AI Agent")


@app.post("/chat")
def chat_endpoint(request: RequestState):
    if request.model_name not in ALLOWED_MODEL_NAMES:
        raise HTTPException(status_code=400, detail="Invalid model name.")
    if request.model_provider not in ALLOWED_PROVIDERS:
        raise HTTPException(status_code=400, detail="Invalid provider.")

    # Build messages list for LangGraph: prepend system prompt
    state_messages = [("system", request.system_prompt)] + [
        (m.role, m.content) for m in request.messages
    ]

    try:
        answer = get_response_from_ai_agent(
            llm_id=request.model_name,
            messages=state_messages,
            allow_search=request.allow_search,
            provider=request.model_provider,
        )
        return {"answer": answer}
    except Exception as e:
        # Send a helpful error instead of a raw 500 traceback
        raise HTTPException(status_code=500, detail=str(e))


# Local dev entrypoint
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9999, reload=True)
