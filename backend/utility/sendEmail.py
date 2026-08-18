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
    raise RuntimeError("RESEND_API_KEY is not set in .env")


if not RESEND_FROM_EMAIL:
    raise RuntimeError("RESEND_FROM_EMAIL is not set in .env")


# ============================================
# Resend Configuration
# ============================================

resend.api_key = RESEND_API_KEY


# ============================================
# Send Email
# ============================================

def send_email(
    requestor_email: str,
    approver_email: str,
    priority: str,
    requestor_message: str
):

    subject = f"PO Desk Approval Request - {priority} Priority"

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

            color: #374151;
        }}

        .requestor-label {{
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

        .portal-button:hover {{
            background-color: #4338ca;
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
                PO Desk Approval Request
            </h1>

            <p>
                A new request requires your review.
            </p>

        </div>


        <!-- ====================================
             Content
        ===================================== -->

        <div class="content">

            <p class="intro">

                You have received a new approval request
                through PO Desk. Please review the request
                and take the appropriate action.

            </p>


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

    try:

        email = resend.Emails.send(
            {
                "from": RESEND_FROM_EMAIL,
                "to": [approver_email],
                "subject": subject,
                "html": html_content,
            }
        )

        return {
            "success": True,
            "email": email
        }

    except Exception as e:

        print(f"Failed to send email: {e}")

        return {
            "success": False,
            "error": str(e)
        }