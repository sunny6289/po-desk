from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session, select

from agents.intake_agent import intake_agent
from agents.prioritization_agent import prioritization_agent
from agents.clarified_requestor_message_agent import (
    clarified_requestor_message_agent
)

from constants.status import RequestStatus

from utility.sendEmail import send_email
from utility.sendRequestorEmail import send_requestor_email

from database.database import (
    create_db_and_tables,
    engine
)

from models.request_model import RequestModel


# ============================================
# FastAPI Application
# ============================================

app = FastAPI()


# ============================================
# CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Request Schemas
# ============================================

class MessageRequest(BaseModel):
    employee_id: int
    employee_email: str
    created_at: datetime
    message: str

# ============================================
# Update Request Status Schema
# ============================================

class UpdateRequestStatus(BaseModel):
    tracking_id: str
    status: RequestStatus
    approver_message: str
    approved_by: int
    approved_at: datetime


class ClarificationAnswer(BaseModel):
    answer: str
    question: str


class ClarificationRequest(BaseModel):
    answers: list[ClarificationAnswer]

    tracking_id: str

    department_name: str
    manager_name: str
    manager_email: str

    clarified_requestor_message: str | None

    user_query: str
    employee_email: str
    message: str

    isRelatedQuery: bool

    need_clarification: bool

    clarifications_required: list[str] | None = None

    status: RequestStatus


class DepartmentRequest(BaseModel):
    department_id: int


# ============================================
# Create Database Tables
# ============================================

create_db_and_tables()


# ============================================
# Home
# ============================================

@app.get("/")
def home():
    return {
        "message": "PO Desk backend is running"
    }


# ============================================
# Send Initial Request
# ============================================

@app.post("/api/chat/send")
def send_message(request: MessageRequest):

    return intake_agent(request)


# ============================================
# Submit Clarifications
# ============================================

@app.post("/api/chat/clarification")
def submit_clarifications(
    request: ClarificationRequest
):

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

    clarified_message = (
        clarified_result.get(
            "clarified_requestor_message"
        )
    )

    # ============================================
    # Call Prioritization Agent
    # ============================================

    prioritization_result = prioritization_agent(
        requestor_message=clarified_message,
        department_name=request.department_name
    )

    # ============================================
    # Send Approval Email
    # ============================================

    try:

        email_result = send_email(
            requestor_email=request.employee_email,
            approver_email=request.manager_email,
            priority=prioritization_result["priority"],
            requestor_message=clarified_message
        )

        print("Email Result:")
        print(email_result)

    except Exception as e:

        print(
            f"Failed to send approval email: {e}"
        )

    # ============================================
    # Update Request Status in DB
    # status: RequestStatus.APPROVAL_PENDING
    # ============================================

    with Session(engine) as session:

        # Find the existing request using tracking_id
        request_record = session.exec(
            select(RequestModel)
            .where(
                RequestModel.tracking_id
                == request.tracking_id
            )
        ).first()

        # ----------------------------------------
        # Request not found
        # ----------------------------------------

        if request_record is None:

            return {
                "message": "Request not found",
                "tracking_id": request.tracking_id
            }

        # ----------------------------------------
        # Update request
        # ----------------------------------------

        request_record.clarified_requestor_message = (
            clarified_message
        )

        request_record.need_clarification = False

        request_record.clarifications_required = None

        request_record.priority = (
            prioritization_result["priority"]
        )

        request_record.average_probability = (
            prioritization_result["average_probability"]
        )

        request_record.status = (
            RequestStatus.APPROVAL_PENDING
        )

        # ----------------------------------------
        # Save changes
        # ----------------------------------------

        session.add(request_record)

        session.commit()

        session.refresh(request_record)

    # ============================================
    # Response
    # ============================================

    return {
        "tracking_id": request.tracking_id,

        "server_message": (
            "Clarifications Sent and "
            "Approval Request Sent Successfully"
        ),

        "department_name": request.department_name,

        "manager_name": request.manager_name,

        "manager_email": request.manager_email,

        "status": RequestStatus.APPROVAL_PENDING,

        "priority": prioritization_result["priority"],

        "average_probability": (
            prioritization_result["average_probability"]
        )
    }


# ============================================
# Get Requests By Department
# ============================================

@app.post("/api/requests/department")
def get_requests_by_department(
    request: DepartmentRequest
):

    with Session(engine) as session:

        requests = session.exec(
            select(RequestModel)
            .where(
                RequestModel.department_id
                == request.department_id
            )
        ).all()

        return requests

# ============================================
# Update Request Status
# ============================================

@app.post("/api/requests/update-status")
def update_request_status(
    request: UpdateRequestStatus
):

    try:

        with Session(engine) as session:

            # Find request
            request_record = session.exec(
                select(RequestModel)
                .where(
                    RequestModel.tracking_id
                    == request.tracking_id
                )
            ).first()

            if request_record is None:
                raise HTTPException(
                    status_code=404,
                    detail="Request not found"
                )

            # ========================================
            # Update database
            # ========================================

            request_record.status = request.status

            request_record.approver_message = (
                request.approver_message
            )

            request_record.approved_by = (
                request.approved_by
            )

            request_record.approved_at = (
                request.approved_at
            )

            session.add(request_record)
            session.commit()
            session.refresh(request_record)

            # ========================================
            # Prepare email data
            # ========================================

            email_data = {
                "tracking_id": request_record.tracking_id,
                "approver_name":
                    request_record.approver_name,

                "approver_employee_id":
                    request_record.approver_employee_id,

                "approver_email":
                    request_record.approver_email,

                "requestor_message":
                    request_record.requestor_message,

                "clarified_requestor_message":
                    request_record.clarified_requestor_message,

                "status":
                    request_record.status.value,

                "approver_message":
                    request_record.approver_message,

                "requestor_email":
                    request_record.requestor_email
            }

        # ========================================
        # Send email AFTER DB transaction is done
        # ========================================

        try:

            email_result = send_requestor_email(
                **email_data
            )

            print("Requestor Email Result:")
            print(email_result)

        except Exception as e:

            print(
                f"Failed to send requestor email: {e}"
            )

            email_result = {
                "success": False,
                "message": "Failed to send requestor email"
            }

        # ========================================
        # Response
        # ========================================

        return {
            "success": True,
            "message": "Request status updated successfully",
            "tracking_id": request_record.tracking_id,
            "status": request_record.status,
            "approved_by": request_record.approved_by,
            "approved_at": request_record.approved_at,
            "approver_message":
                request_record.approver_message,
            "email_sent":
                email_result.get("success", False)
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            "Database error while updating "
            f"request status: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update request status"
        )


@app.get("/api/requests/requestor/{requestor_id}")
def get_requests_by_requestor(requestor_id: int):

    with Session(engine) as session:

        requests = session.exec(
            select(RequestModel)
            .where(
                RequestModel.requestor_id == requestor_id
            )
        ).all()

        return requests