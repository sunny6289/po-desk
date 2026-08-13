from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.intake_agent import intake_agent


app = FastAPI()


# Allow React frontend to access FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "PO Desk backend is running"
    }


@app.post("/api/chat/send")
def send_message(request: MessageRequest):
    return intake_agent(request.message)