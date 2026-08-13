from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.intake_agent import intake_agent
from agents.clarified_requestor_message_agent import (
    clarified_requestor_message_agent
)
from constants.status import RequestStatus


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    employee_id: int
    employee_email: str
    created_at: str
    message: str


class ClarificationAnswer(BaseModel):
    answer: str
    question: str


class ClarificationRequest(BaseModel):
    answers: list[ClarificationAnswer]

    tracking_id: str

    department_name: str
    manager_name: str
    manager_email: str

    user_query: str
    message: str

    isRelatedQuery: bool

    need_clarification: bool
    clarifications_required: list[str] | None = None

    status: RequestStatus


@app.get("/")
def home():
    return {
        "message": "PO Desk backend is running"
    }


@app.post("/api/chat/send")
def send_message(request: MessageRequest):
    return intake_agent(request.message)


@app.post("/api/chat/clarification")
def submit_clarifications(request: ClarificationRequest):

    # ============================================
    # Generate clarified requestor message
    # ============================================

    clarified_result = clarified_requestor_message_agent(
        user_query=request.user_query,
        answers=request.answers
    )

    # ============================================
    # Get clarified requestor message
    # ============================================

    clarified_requestor_message = (
        clarified_result.get("clarified_requestor_message")
    )

    # ============================================
    # Print for debugging
    # ============================================

    print("Clarified Requestor Message:")
    print(clarified_requestor_message)

    # ============================================
    # Response
    # ============================================

    return {
        "message": "Clarifications received successfully",
        "tracking_id": request.tracking_id,
        "answers": request.answers,
        "clarified_requestor_message": clarified_requestor_message,
        "status": request.status
    }