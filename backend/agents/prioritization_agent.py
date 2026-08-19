import json
import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field


# ============================================
# Environment
# ============================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in .env")


# ============================================
# Load Severity Metrics
# ============================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

SEVERITY_METRICS_PATH = os.path.join(
    BASE_DIR,
    "severity_metrics.json"
)

with open(
    SEVERITY_METRICS_PATH,
    "r",
    encoding="utf-8"
) as file:
    severity_metrics = json.load(file)


# ============================================
# Gemini Client
# ============================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================
# Gemini Response Schema
# ============================================

class MetricProbability(BaseModel):
    metric: str
    probability: float = Field(
        ge=0,
        le=100
    )


class PrioritizationResult(BaseModel):
    metrics: list[MetricProbability]


# ============================================
# Prioritization Agent
# ============================================

def prioritization_agent(
    requestor_message: str,
    department_name: str
):

    # ========================================
    # Find Department Metrics
    # ========================================

    department_metrics = next(
        (
            department
            for department in severity_metrics
            if department["department_name"] == department_name
        ),
        None
    )

    # ========================================
    # Invalid Department
    # ========================================

    if department_metrics is None:

        return {
            "success": False,
            "message": (
                f"No severity metrics found for department: "
                f"{department_name}"
            )
        }

    metrics = department_metrics["metrics"]


    # ========================================
    # Gemini Prompt
    # ========================================

    prompt = f"""
You are a Prioritization Agent for a company's internal PO Desk.

Your job is to analyze an employee's request and estimate the
possibility that each severity metric is relevant to the request.

Department:

{department_name}

Employee Request:

{requestor_message}

Severity Metrics for this department:

{json.dumps(metrics, indent=2)}


For EACH metric:

1. Analyze the employee's request.
2. Determine how strongly the request indicates that this
   metric may be relevant to the incident/request.
3. Assign a probability from 0 to 100.

Interpretation:

0 means there is essentially no indication that the metric
is relevant.

100 means the request strongly indicates that the metric
is relevant.

Important rules:

- Evaluate every metric.
- Return exactly one probability for every metric.
- Do not omit any metric.
- Do not invent additional metrics.
- Use only the metrics provided above.
- Base the probability only on the information present
  in the employee's request.
- Do not assume facts that are not present.
- A vague request should generally result in lower
  probabilities.
- A request explicitly mentioning a metric should result
  in a higher probability.
- Return probabilities as numbers from 0 to 100.
- Do not include the % symbol in the probability value.


Example:

If the request is:

"Payment failures have increased significantly and
customers are unable to complete checkout."

A metric such as:

"Transaction failure rate (percentage of failed payments)"

could have a high probability.

A metric such as:

"Number of pending refunds exceeding 24 hours"

would have a lower probability if refunds are not mentioned.


Return exactly one structured response containing
all {len(metrics)} metrics.
"""


    # ========================================
    # Call Gemini
    # ========================================

    try:

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": (
                    PrioritizationResult.model_json_schema()
                ),
            },
        )


        # ====================================
        # Parse Response
        # ====================================

        result = PrioritizationResult.model_validate_json(
            response.text
        )


    except Exception as e:

        print(
            f"Prioritization Agent error: {e}"
        )

        return {
            "success": False,
            "message": (
                "Unable to prioritize the request right now."
            )
        }


    # ========================================
    # Validate Metrics
    # ========================================

    returned_metrics = result.metrics

    if len(returned_metrics) != len(metrics):

        return {
            "success": False,
            "message": (
                "Prioritization Agent returned an "
                "invalid number of metrics."
            )
        }


    # ========================================
    # Calculate Average
    # ========================================

    total_probability = sum(
        metric.probability
        for metric in returned_metrics
    )

    average_probability = (
        total_probability / len(returned_metrics)
    )


    # ========================================
    # Determine Priority
    # ========================================

    if average_probability <= 50:

        priority = "LOW"

    elif average_probability <= 70:

        priority = "MEDIUM"

    else:

        priority = "HIGH"


    # ========================================
    # Determine Reply Within
    # ========================================

    if priority == "LOW":

        reply_within = 30

    elif priority == "MEDIUM":

        reply_within = 20

    else:

        reply_within = 10


    # ========================================
    # Build Response
    # ========================================

    return {
        "success": True,

        "department_name": department_name,

        "metrics": [
            {
                "metric": metric.metric,
                "probability": metric.probability
            }
            for metric in returned_metrics
        ],

        "average_probability": round(
            average_probability,
            2
        ),

        "priority": priority,

        "reply_within": reply_within
    }