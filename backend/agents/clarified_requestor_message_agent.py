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
# Input Model
# ============================================

class ClarificationAnswer(BaseModel):
    question: str
    answer: str


# ============================================
# Gemini Response Schema
# ============================================

class ClarifiedRequestResult(BaseModel):
    clarified_requestor_message: str


# ============================================
# Clarified Requestor Message Agent
# ============================================

def clarified_requestor_message_agent(
    user_query: str,
    answers: list[ClarificationAnswer]
):

    clarification_data = "\n".join(
        f"Question: {item.question}\n"
        f"Answer: {item.answer}"
        for item in answers
    )

    prompt = f"""
You are a Clarified Request Builder Agent for a company's
internal PO Desk.

Your job is to create a clear, complete, and actionable version
of the employee's original request by combining:

1. The original user query
2. The answers provided by the employee to clarification questions

You MUST preserve all important information from the original
user query.

You MUST incorporate all relevant information provided in the
clarification answers.

Do not remove important details from the original request.

Do not invent information that was not provided by the employee.

Do not change the meaning or intent of the original request.

The resulting request should be written as a single clear message
that can be directly given to the relevant department or
development team.

Do not mention that clarification questions were asked.

Do not include phrases such as:
- "The user originally said..."
- "The user clarified..."
- "According to the answers..."
- "The employee responded..."

Instead, write the final request naturally as if the employee had
provided all of the information in their original request.

--------------------------------------------
Original User Query
--------------------------------------------

{user_query}


--------------------------------------------
Clarification Questions and Answers
--------------------------------------------

{clarification_data}


--------------------------------------------
Output Requirements
--------------------------------------------

Return ONLY a structured response containing:

clarified_requestor_message

The clarified request must:

- Preserve the original request's intent.
- Include all important information from the original query.
- Include all relevant clarification answers.
- Be specific and actionable.
- Be concise enough for a department/development team to understand.
- Never invent missing information.
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
                "response_json_schema": (
                    ClarifiedRequestResult.model_json_schema()
                ),
            },
        )

        # ========================================
        # Parse structured response
        # ========================================

        result = ClarifiedRequestResult.model_validate_json(
            response.text
        )

        return {
            "clarified_requestor_message": (
                result.clarified_requestor_message
            )
        }

    except Exception as e:

        print(
            f"Clarified Requestor Message Agent error: {e}"
        )

        return {
            "clarified_requestor_message": None
        }