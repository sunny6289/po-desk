import json
import os
import uuid

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

from agents.clarification_agent import clarification_agent
from constants.status import RequestStatus


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
# Gemini Response Schema
# ============================================

class IntakeResult(BaseModel):
    is_request: bool
    department_name: str | None


# ============================================
# Intake Agent
# ============================================

def intake_agent(message: str):

    department_names = [
        department["department_name"]
        for department in departments
    ]

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

{message}
"""

    try:

        # ========================================
        # Ask Gemini
        # ========================================

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": IntakeResult.model_json_schema(),
            },
        )

        # ========================================
        # Parse structured response
        # ========================================

        result = IntakeResult.model_validate_json(
            response.text
        )

        is_request = result.is_request
        department_name = result.department_name

    except Exception as e:

        print(f"Intake Agent error: {e}")

        return {
            "isRelatedQuery": False,
            "user_query": message,
            "server_message": "Unable to process the request right now."
        }

    # ============================================
    # Request / Department validation
    # ============================================

    if not is_request or not department_name:

        return {
            "isRelatedQuery": False,
            "user_query": message,
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
            "user_query": message,
            "server_message": (
                "Please request related to the below departments: "
                + ", ".join(department_names)
            )
        }

    # ============================================
    # Generate Tracking ID
    # ============================================

    tracking_id = "PO-" + str(uuid.uuid4())[-10:].upper()

    # ============================================
    # Call Clarification Agent
    # ============================================

    try:

        clarification_result = clarification_agent(
            department_name=department_name,
            user_query=message
        )

    except Exception as e:

        print(f"Clarification Agent error: {e}")

        return {
            "isRelatedQuery": False,
            "user_query": message,
            "server_message": "Unable to process the request right now."
        }

    # ============================================
    # Base Successful Payload
    # ============================================

    response_payload = {
        "tracking_id": tracking_id,
        "department_name": selected_department["department_name"],
        "manager_name": selected_department["manager_name"],
        "manager_email": selected_department["manager_email"],
        "server_message": "Request sent successfully",
        "user_query": message,
        "isRelatedQuery": True
    }

    # ============================================
    # Clarification Required
    # ============================================

    if clarification_result.get("need_clarification") is True:

        response_payload["need_clarification"] = True

        response_payload["clarifications_required"] = (
            clarification_result.get(
                "clarifications_required",
                []
            )
        )

        response_payload["status"] = RequestStatus.NEED_CLARIFICATION

        return response_payload

    # ============================================
    # No Clarification Required
    # ============================================

    response_payload["need_clarification"] = False
    response_payload["clarifications_required"] = None
    response_payload["status"] = RequestStatus.APPROVAL_PENDING

    return response_payload