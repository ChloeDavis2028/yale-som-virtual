"""FastAPI backend: chat with AI avatars of Yale SOM professors.

    backend/.venv/Scripts/python -m uvicorn main:app --app-dir backend --port 8000

Routes: GET /api/health, GET /api/people, POST /api/people/{person_id}/chat
"""

from __future__ import annotations

import uuid
from collections import OrderedDict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_ai.messages import ModelMessage, ModelRequest, UserPromptPart

from people import MODEL_NAME, PEOPLE, agent_for

MAX_SESSIONS = 200
MAX_MESSAGES = 40

app = FastAPI(title="Yale SOM Virtual: AI avatars")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# (person_id, session_id) -> PydanticAI message history, oldest session first
SESSIONS: OrderedDict[tuple[str, str], list[ModelMessage]] = OrderedDict()


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None


class ChatOut(BaseModel):
    reply: str
    session_id: str


def _is_user_turn(msg: ModelMessage) -> bool:
    return isinstance(msg, ModelRequest) and any(isinstance(p, UserPromptPart) for p in msg.parts)


def _trim(history: list[ModelMessage]) -> list[ModelMessage]:
    """Keep about the last MAX_MESSAGES, cutting only where a user turn starts so tool calls stay paired."""
    if len(history) <= MAX_MESSAGES:
        return history
    for i in range(len(history) - MAX_MESSAGES, len(history)):
        if _is_user_turn(history[i]):
            return history[i:]
    return []


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "model": MODEL_NAME, "people": list(PEOPLE)}


@app.get("/api/people")
def people() -> list[dict]:
    return [
        {"id": p.id, "name": p.name, "title": p.title, "room": p.room, "course": p.course_number}
        for p in PEOPLE.values()
    ]


@app.post("/api/people/{person_id}/chat", response_model=ChatOut)
async def chat(person_id: str, body: ChatIn) -> ChatOut:
    if person_id not in PEOPLE:
        raise HTTPException(status_code=404, detail=f"No avatar called '{person_id}'.")
    session_id = body.session_id or uuid.uuid4().hex
    key = (person_id, session_id)
    history = _trim(SESSIONS.get(key, []))
    try:
        result = await agent_for(person_id).run(body.message, message_history=history)
    except Exception as exc:  # model / network / Portkey failure
        raise HTTPException(status_code=502, detail=f"The AI model call failed: {type(exc).__name__}") from exc
    SESSIONS[key] = result.all_messages()
    SESSIONS.move_to_end(key)
    while len(SESSIONS) > MAX_SESSIONS:
        SESSIONS.popitem(last=False)
    return ChatOut(reply=result.output, session_id=session_id)
