import json
import os
import uuid

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from sqlmodel import Session, select
from datetime import datetime, timedelta

from agents.clarification_agent import clarification_agent
from agents.prioritization_agent import prioritization_agent
from constants.status import RequestStatus
from models.request_model import RequestModel
from utility.sendEmail import send_email
from database.database import engine


# ============================================
# Environment
# ============================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in .env")


# ============================================
# Load Knowledge Base
# ============================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

KNOWLEDGE_BASE_PATH = os.path.join(
    BASE_DIR,
    "departments_knowledge_base.json"
)

with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:
    knowledge_base = json.load(file)

departments = knowledge_base["departments"]


# ============================================
# Gemini Client
# ============================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================
# Message Request Schema
# ============================================

class MessageRequest(BaseModel):
    employee_id: int
    employee_email: str
    created_at: str
    message: str


# ============================================
# Gemini Response Schema
# ============================================

class IntakeResult(BaseModel):
    is_request: bool
    department_name: str | None


# ============================================
# Intake Agent
# ============================================

def intake_agent(user_request: MessageRequest):

    department_names = [
        department["department_name"]
        for department in departments
    ]

    # ============================================
    # Intake Prompt
    # ============================================

    prompt = f"""
You are an Intake Agent for a company's internal PO Desk.

Analyze the employee's message and determine:

1. Whether the employee is asking for help, a solution,
   an action, or assistance.

2. If it is a request, determine whether it belongs to
   one of the departments in the knowledge base.

Knowledge Base:

{json.dumps(knowledge_base, indent=2)}

Rules:

- Greetings and casual conversation are NOT requests.
- Questions or problems requiring help ARE requests.
- Only select a department from the knowledge base.
- Never invent a department.
- Return the exact department_name from the knowledge base.
- If the message is not a request, department_name must be null.
- If the message is a request but doesn't belong to any
  department, department_name must be null.

Employee message:

{user_request.message}
"""

    # ============================================
    # Ask Gemini
    # ============================================

    try:

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": (
                    IntakeResult.model_json_schema()
                ),
            },
        )

        result = IntakeResult.model_validate_json(
            response.text
        )

        is_request = result.is_request
        department_name = result.department_name

    except Exception as e:

        print(f"Intake Agent error: {e}")

        return {
            "isRelatedQuery": False,
            "user_query": user_request.message,
            "server_message": (
                "Unable to process the request right now."
            )
        }

    # ============================================
    # Request / Department validation
    # ============================================

    if not is_request or not department_name:

        return {
            "isRelatedQuery": False,
            "user_query": user_request.message,
            "server_message": (
                "Please request related to the below departments: "
                + ", ".join(department_names)
            )
        }

    # ============================================
    # Find Department
    # ============================================

    selected_department = next(
        (
            department
            for department in departments
            if department["department_name"] == department_name
        ),
        None
    )

    # ============================================
    # Invalid Department
    # ============================================

    if selected_department is None:

        return {
            "isRelatedQuery": False,
            "user_query": user_request.message,
            "server_message": (
                "Please request related to the below departments: "
                + ", ".join(department_names)
            )
        }

    # ============================================
    # Generate Tracking ID
    # ============================================

    tracking_id = (
        "PO-" + str(uuid.uuid4())[-10:].upper()
    )

    # ============================================
    # Create initial DB record
    # Status: CLASSIFIED
    # ============================================

    request_record = RequestModel(
        requestor_id=user_request.employee_id,
        requestor_email=user_request.employee_email,

        created_at=user_request.created_at,

        requestor_message=user_request.message,
        clarified_requestor_message=None,

        tracking_id=tracking_id,

        status=RequestStatus.CLASSIFIED,

        department_id=selected_department["department_id"],
        department_name=selected_department["department_name"],

        approver_employee_id=(
            selected_department["manager_employee_id"]
        ),
        approver_name=selected_department["manager_name"],
        approver_email=selected_department["manager_email"],

        senior_manager_employee_id=(selected_department["senior_manager_employee_id"]),
        senior_manager_name=selected_department["senior_manager_name"],
        senior_manager_email=selected_department["senior_manager_email"],

        need_clarification=False,
        clarifications_required=None,

        priority=None,
        average_probability=None,

        approved_by=None,
        approved_at=None,
        approver_message=None,
        reply_within=None,
        reply_deadline=None
    )

    # ============================================
    # Save initial record
    # ============================================

    try:

        with Session(engine) as session:

            session.add(request_record)
            session.commit()
            session.refresh(request_record)

    except Exception as e:

        print(f"Database error while creating request: {e}")

        return {
            "isRelatedQuery": False,
            "user_query": user_request.message,
            "server_message": (
                "Unable to save the request right now."
            )
        }

    # ============================================
    # Call Clarification Agent
    # ============================================

    try:

        clarification_result = clarification_agent(
            department_name=department_name,
            user_query=user_request.message
        )

    except Exception as e:

        print(f"Clarification Agent error: {e}")

        return {
            "isRelatedQuery": False,
            "user_query": user_request.message,
            "server_message": (
                "Unable to process the request right now."
            )
        }

    # ============================================
    # Base Response Payload
    # ============================================

    response_payload = {
        "tracking_id": tracking_id,
        "department_name": (
            selected_department["department_name"]
        ),
        "manager_name": (
            selected_department["manager_name"]
        ),
        "manager_email": (
            selected_department["manager_email"]
        ),
        "server_message": (
            "Approval Request sent successfully"
        ),
        "clarified_requestor_message": None,
        "user_query": user_request.message,
        "isRelatedQuery": True,
        "employee_email": user_request.employee_email
    }

    # ============================================
    # Clarification Required
    # ============================================

    if clarification_result.get(
        "need_clarification"
    ) is True:

        clarifications_required = (
            clarification_result.get(
                "clarifications_required",
                []
            )
        )

        # ============================================
        # Update DB
        # Status: NEED_CLARIFICATION
        # ============================================

        try:

            with Session(engine) as session:

                request_record = session.get(
                    RequestModel,
                    request_record.id
                )

                request_record.status = (
                    RequestStatus.NEED_CLARIFICATION
                )

                request_record.need_clarification = True

                request_record.clarifications_required = (
                    json.dumps(clarifications_required)
                )

                session.add(request_record)
                session.commit()

        except Exception as e:

            print(
                "Database error while updating "
                f"clarification status: {e}"
            )

            return {
                "isRelatedQuery": False,
                "user_query": user_request.message,
                "server_message": (
                    "Unable to update request status."
                )
            }

        # ============================================
        # Response
        # ============================================

        response_payload["need_clarification"] = True

        response_payload["clarifications_required"] = (
            clarifications_required
        )

        response_payload["status"] = (
            RequestStatus.NEED_CLARIFICATION
        )

        return response_payload

    # ============================================
    # No Clarification Required
    # ============================================

    try:

        prioritization_result = prioritization_agent(
            requestor_message=user_request.message,
            department_name=department_name
        )

        print("Prioritization Result:")
        print(prioritization_result)

    except Exception as e:

        print(f"Prioritization Agent error: {e}")

        return {
            "isRelatedQuery": False,
            "user_query": user_request.message,
            "server_message": (
                "Unable to process the request right now."
            )
        }

    # ============================================
    # Validate Prioritization Result
    # ============================================

    if not prioritization_result.get("success"):

        print(
            "Prioritization Agent failed:",
            prioritization_result
        )

        return {
            "isRelatedQuery": False,
            "user_query": user_request.message,
            "server_message": (
                "Unable to prioritize the request right now."
            )
        }

    # ============================================
    # Get Priority Information
    # ============================================

    average_probability = (
        prioritization_result[
            "average_probability"
        ]
    )

    priority = prioritization_result["priority"]
    reply_within = prioritization_result["reply_within"]

    # ============================================
    # Update DB
    # Status: PRIORITIZED
    # ============================================

    try:

        with Session(engine) as session:

            request_record = session.get(
                RequestModel,
                request_record.id
            )

            request_record.status = (
                RequestStatus.PRIORITIZED
            )

            request_record.need_clarification = False

            request_record.clarifications_required = None

            request_record.average_probability = (
                average_probability
            )

            request_record.priority = priority
            request_record.reply_within = reply_within

            request_record.reply_deadline = (
                datetime.now()
                + timedelta(seconds=reply_within)
            )
            session.add(request_record)
            session.commit()

    except Exception as e:

        print(
            "Database error while updating "
            f"prioritization: {e}"
        )

        return {
            "isRelatedQuery": False,
            "user_query": user_request.message,
            "server_message": (
                "Unable to update request prioritization."
            )
        }

    # ============================================
    # Final Response
    # ============================================

    response_payload["need_clarification"] = False

    response_payload["clarifications_required"] = None

    response_payload["status"] = (
        RequestStatus.APPROVAL_PENDING
    )

    response_payload["average_probability"] = (
        average_probability
    )

    response_payload["priority"] = priority

    # ============================================
    # Send Approval Email
    # ============================================

    try:

        email_result = send_email(
            requestor_email=user_request.employee_email,
            approver_email=(
                selected_department["manager_email"]
            ),
            priority=priority,
            requestor_message=user_request.message
        )

        print("Email Result:")
        print(email_result)

    except Exception as e:

        print(f"Failed to send approval email: {e}")

    # ============================================
    # Update DB
    # Status: APPROVAL_PENDING
    # ============================================

    try:

        with Session(engine) as session:

            request_record = session.exec(
                select(RequestModel).where(
                    RequestModel.tracking_id == tracking_id
                )
            ).first()

            if request_record is None:
                print(
                    f"Request not found: {tracking_id}"
                )

            else:

                request_record.status = (
                    RequestStatus.APPROVAL_PENDING
                )

                session.add(request_record)
                session.commit()

    except Exception as e:

        print(
            "Database error while updating "
            f"approval status: {e}"
        )

    return response_payload