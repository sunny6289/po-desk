import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


# ============================================
# Environment
# ============================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in .env")


# ============================================
# Gemini Client
# ============================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================
# Gemini Response Schema
# ============================================

class ClarificationResult(BaseModel):
    need_clarification: bool
    clarifications_required: list[str] | None = None


# ============================================
# Clarification Agent
# ============================================

def clarification_agent(
    department_name: str,
    user_query: str
):

    prompt = f"""
You are a Clarification Agent for a company's internal PO Desk.

Your job is to determine whether the user's request contains
enough information for the relevant department or development
team to start working on the request.

Department:

{department_name}

User Query:

{user_query}

Your task:

Analyze the user's query and determine whether any important
information is missing that could be crucial for the department
or development team to understand, investigate, implement,
or solve the request.

Ask for clarification when information such as the following
is necessary:

- Current state or current value
- Expected or desired value
- Specific quantity or limit
- Reason or business justification
- Relevant dates or deadlines
- Affected users, accounts, products, orders, or transactions
- Error messages or error details
- Steps to reproduce a problem
- Relevant IDs or references
- Environment or system information
- Any other information that is necessary to properly work
  on the request

Important rules:

1. Do NOT ask unnecessary questions.
2. Only ask questions whose answers would materially help
   the department work on the request.
3. If the request already contains sufficient information,
   do not ask for clarification.
4. Questions should be specific to the user's request and
   department.
5. Do not ask questions that the department can determine
   themselves without needing the user.
6. If clarification is required, ask only the minimum
   necessary questions.
7. Return only the structured response.

Example 1:

User query:

"Increase payment limit"

Return:

{{
    "need_clarification": true,
    "clarifications_required": [
        "What is the current payment limit?",
        "How much do we need to increase the payment limit?",
        "Why do we need to increase the payment limit?"
    ]
}}

Example 2:

User query:

"We need to increase the payment limit till $3000 from $1200
because of the upcoming Friday sale."

Return:

{{
    "need_clarification": false,
    "clarifications_required": null
}}

Return exactly one structured response.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": (
                    ClarificationResult.model_json_schema()
                ),
            },
        )

        result = ClarificationResult.model_validate_json(
            response.text
        )

        if result.need_clarification:

            return {
                "need_clarification": True,
                "clarifications_required": (
                    result.clarifications_required
                )
            }

        return {
            "need_clarification": False,
            "clarifications_required": None
        }

    except Exception as e:

        print(f"Clarification Agent error: {e}")

        return {
            "need_clarification": False,
            "clarifications_required": None
        }