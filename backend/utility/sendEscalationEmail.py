import os

import resend
from dotenv import load_dotenv


# ============================================
# Environment
# ============================================

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL")


if not RESEND_API_KEY:
    raise RuntimeError(
        "RESEND_API_KEY is not set in .env"
    )

if not RESEND_FROM_EMAIL:
    raise RuntimeError(
        "RESEND_FROM_EMAIL is not set in .env"
    )


resend.api_key = RESEND_API_KEY


# ============================================
# Send Escalation Email
# ============================================

def send_escalation_email(
    senior_manager_name: str,
    senior_manager_employee_id: int,
    senior_manager_email: str,
    requestor_message: str,
    requestor_email: str,
    tracking_id: str,
    priority: str,
    reply_within: int | None = None
):

    # ========================================
    # HTML Content
    # ========================================

    deadline_text = ""

    if reply_within is not None:

        deadline_text = f"""
        <p class="deadline">
            This request has been escalated because the
            previous approver did not respond within the
            required time.
        </p>
        """

    html_content = f"""
    <html>

    <head>

        <style>

            body {{
                margin: 0;
                padding: 0;

                background-color: #f5f7fa;

                font-family:
                    Arial,
                    Helvetica,
                    sans-serif;

                color: #1f2937;
            }}

            .email-container {{
                max-width: 650px;

                margin: 30px auto;

                background-color: #ffffff;

                border: 1px solid #e5e7eb;

                border-radius: 10px;

                overflow: hidden;
            }}

            /* ========================================
               Header
            ======================================== */

            .header {{
                padding: 24px 28px;

                border-bottom: 1px solid #e5e7eb;
            }}

            .header h1 {{
                margin: 0;

                font-size: 22px;

                color: #111827;
            }}

            .header p {{
                margin: 7px 0 0;

                font-size: 14px;

                color: #6b7280;
            }}

            /* ========================================
               Content
            ======================================== */

            .content {{
                padding: 28px;
            }}

            .intro {{
                margin: 0 0 24px;

                font-size: 14px;

                line-height: 1.6;

                color: #374151;
            }}

            /* ========================================
               Section
            ======================================== */

            .section {{
                margin-bottom: 24px;
            }}

            .section-title {{
                margin: 0 0 10px;

                font-size: 14px;

                font-weight: 700;

                color: #374151;
            }}

            /* ========================================
               Priority
            ======================================== */

            .priority-badge {{
                display: inline-block;

                padding: 7px 14px;

                border-radius: 999px;

                font-size: 13px;

                font-weight: 700;
            }}

            .priority-low {{
                background-color: #dcfce7;

                color: #166534;
            }}

            .priority-medium {{
                background-color: #fef3c7;

                color: #92400e;
            }}

            .priority-high {{
                background-color: #fee2e2;

                color: #991b1b;
            }}

            /* ========================================
               Escalation
            ======================================== */

            .escalation-box {{
                padding: 14px 16px;

                background-color: #fff7ed;

                border-left: 4px solid #f97316;

                border-radius: 6px;

                font-size: 14px;

                line-height: 1.6;

                color: #9a3412;
            }}

            /* ========================================
               Request
            ======================================== */

            .request-box {{
                padding: 16px;

                background-color: #f9fafb;

                border-left: 4px solid #6366f1;

                border-radius: 6px;

                font-size: 14px;

                line-height: 1.6;

                color: #374151;
            }}

            /* ========================================
               Requestor
            ======================================== */

            .requestor-box {{
                padding: 14px 16px;

                background-color: #f9fafb;

                border-radius: 6px;

                font-size: 14px;

                line-height: 1.6;

                color: #374151;
            }}

            .requestor-label {{
                font-weight: 700;

                color: #6b7280;
            }}

            /* ========================================
               Approver
            ======================================== */

            .approver-box {{
                padding: 14px 16px;

                background-color: #f9fafb;

                border-radius: 6px;

                font-size: 14px;

                line-height: 1.7;

                color: #374151;
            }}

            .approver-label {{
                font-weight: 700;

                color: #6b7280;
            }}

            /* ========================================
               Portal Button
            ======================================== */

            .portal-container {{
                text-align: center;

                margin-top: 30px;
            }}

            .portal-button {{
                display: inline-block;

                padding: 11px 20px;

                background-color: #4f46e5;

                color: #ffffff !important;

                text-decoration: none;

                border-radius: 7px;

                font-size: 14px;

                font-weight: 600;
            }}

            /* ========================================
               Footer
            ======================================== */

            .footer {{
                padding: 20px 28px;

                background-color: #f9fafb;

                border-top: 1px solid #e5e7eb;

                text-align: center;
            }}

            .footer p {{
                margin: 0;

                font-size: 12px;

                color: #9ca3af;
            }}

        </style>

    </head>


    <body>

        <div class="email-container">


            <!-- ====================================
                 Header
            ===================================== -->

            <div class="header">

                <h1>
                    PO Desk Request Escalated
                </h1>

                <p>
                    A request requires your immediate review.
                </p>

            </div>


            <!-- ====================================
                 Content
            ===================================== -->

            <div class="content">

                <p class="intro">

                    Hello {senior_manager_name},

                    a PO Desk approval request has been
                    escalated to you because the previous
                    approver did not respond within the
                    required time.

                </p>


                <!-- Escalation -->

                <div class="section">

                    <div class="escalation-box">

                        <strong>
                            Action Required
                        </strong>

                        <br>

                        You are now the approver for this request.

                    </div>

                </div>


                {deadline_text}


                <!-- Tracking ID -->

                <div class="section">

                    <h3 class="section-title">
                        Request ID
                    </h3>

                    <div class="requestor-box">

                        <strong>
                            {tracking_id}
                        </strong>

                    </div>

                </div>


                <!-- Priority -->

                <div class="section">

                    <h3 class="section-title">
                        Priority
                    </h3>

                    <span class="priority-badge
                        {
                            "priority-low"
                            if priority == "LOW"
                            else
                            "priority-medium"
                            if priority == "MEDIUM"
                            else
                            "priority-high"
                        }
                    ">

                        {priority}

                    </span>

                </div>


                <!-- Request -->

                <div class="section">

                    <h3 class="section-title">
                        Request
                    </h3>

                    <div class="request-box">

                        {requestor_message}

                    </div>

                </div>


                <!-- Requestor -->

                <div class="section">

                    <h3 class="section-title">
                        Requestor
                    </h3>

                    <div class="requestor-box">

                        <span class="requestor-label">
                            Email:
                        </span>

                        {requestor_email}

                    </div>

                </div>


                <!-- New Approver -->

                <div class="section">

                    <h3 class="section-title">
                        You are now the approver
                    </h3>

                    <div class="approver-box">

                        <div>
                            <span class="approver-label">
                                Name:
                            </span>

                            {senior_manager_name}
                        </div>

                        <div>
                            <span class="approver-label">
                                Employee ID:
                            </span>

                            {senior_manager_employee_id}
                        </div>

                        <div>
                            <span class="approver-label">
                                Email:
                            </span>

                            {senior_manager_email}
                        </div>

                    </div>

                </div>


                <!-- Portal -->

                <div class="portal-container">

                    <a
                        href="http://localhost:5174/"
                        target="_blank"
                        class="portal-button"
                    >
                        Open PO Desk Portal
                    </a>

                </div>

            </div>


            <!-- ====================================
                 Footer
            ===================================== -->

            <div class="footer">

                <p>
                    This email was automatically sent by PO Desk.
                </p>

                <p style="margin-top: 5px;">

                    Please do not reply to this email.

                </p>

            </div>


        </div>

    </body>

    </html>
    """


    # ========================================
    # Send Email Through Resend
    # ========================================

    try:

        response = resend.Emails.send(
            {
                "from": RESEND_FROM_EMAIL,
                "to": [senior_manager_email],
                "subject": (
                    f"[PO Desk] Request {tracking_id} "
                    f"Escalated - {priority} Priority"
                ),
                "html": html_content
            }
        )

        return {
            "success": True,
            "message": "Escalation email sent successfully",
            "response": response
        }

    except Exception as e:

        print(
            f"Failed to send escalation email: {e}"
        )

        return {
            "success": False,
            "message": "Failed to send escalation email",
            "error": str(e)
        }