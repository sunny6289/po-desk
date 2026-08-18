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
# Send Requestor Email
# ============================================

def send_requestor_email(
    tracking_id: int,
    approver_name: str,
    approver_employee_id: int,
    approver_email: str,
    requestor_message: str,
    clarified_requestor_message: str | None,
    status: str,
    approver_message: str,
    requestor_email: str
):

    # ============================================
    # Select Request Message
    # ============================================

    final_requestor_message = (
        clarified_requestor_message
        if clarified_requestor_message
        else requestor_message
    )

    # ============================================
    # Status Text
    # ============================================

    if status == "APPROVED":
        status_text = "Approved"
    elif status == "REJECTED":
        status_text = "Rejected"
    else:
        status_text = status

    # ============================================
    # Email Subject
    # ============================================

    subject = (
        f"PO Desk Request {status_text}"
    )

    # ============================================
    # Email HTML
    # ============================================

    html = f"""
<html>
<head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #f5f7fa;
            font-family: Arial, Helvetica, sans-serif;
            color: #1f2937;
        }}

        .email-container {{
            max-width: 650px;
            margin: 30px auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #e5e7eb;
        }}

        .header {{
            padding: 24px 28px;
            background-color: #ffffff;
            border-bottom: 1px solid #e5e7eb;
        }}

        .header h1 {{
            margin: 0;
            font-size: 22px;
            color: #111827;
        }}

        .header p {{
            margin: 6px 0 0;
            font-size: 14px;
            color: #6b7280;
        }}

        .content {{
            padding: 28px;
        }}

        .status-container {{
            text-align: center;
            margin-bottom: 28px;
        }}

        .status-badge {{
            display: inline-block;
            padding: 7px 16px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: bold;
        }}

        .status-approved {{
            background-color: #dcfce7;
            color: #166534;
        }}

        .status-rejected {{
            background-color: #fee2e2;
            color: #991b1b;
        }}

        .request-id {{
            margin-top: 12px;
            font-family: monospace;
            font-size: 14px;
            color: #4b5563;
        }}

        .section {{
            margin-bottom: 24px;
        }}

        .section-title {{
            margin: 0 0 10px;
            font-size: 14px;
            font-weight: bold;
            color: #374151;
        }}

        .request-message {{
            padding: 16px;
            background-color: #f9fafb;
            border-left: 4px solid #6366f1;
            border-radius: 6px;
            font-size: 14px;
            line-height: 1.6;
            color: #374151;
        }}

        .details {{
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }}

        .detail-row {{
            display: table;
            width: 100%;
            border-bottom: 1px solid #e5e7eb;
        }}

        .detail-row:last-child {{
            border-bottom: none;
        }}

        .detail-label {{
            display: table-cell;
            width: 35%;
            padding: 12px 14px;
            background-color: #f9fafb;
            font-size: 13px;
            font-weight: bold;
            color: #6b7280;
        }}

        .detail-value {{
            display: table-cell;
            padding: 12px 14px;
            font-size: 13px;
            color: #1f2937;
        }}

        .approver-message {{
            padding: 16px;
            background-color: #f9fafb;
            border-radius: 6px;
            font-size: 14px;
            line-height: 1.6;
            color: #374151;
        }}

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

        <!-- Header -->

        <div class="header">

            <h1>PO Desk Request Update</h1>

            <p>
                Your request has been reviewed by the approver.
            </p>

        </div>


        <!-- Content -->

        <div class="content">

            <!-- Status -->

            <div class="status-container">

                <div class="status-badge
                    {
                        "status-approved"
                        if status == "APPROVED"
                        else "status-rejected"
                    }
                ">
                    {status_text}
                </div>

                <div class="request-id">
                    Request ID: {tracking_id}
                </div>

            </div>


            <!-- Request -->

            <div class="section">

                <h3 class="section-title">
                    Your Request
                </h3>

                <div class="request-message">
                    {final_requestor_message}
                </div>

            </div>


            <!-- Approver Details -->

            <div class="section">

                <h3 class="section-title">
                    Approver Details
                </h3>

                <div class="details">

                    <div class="detail-row">

                        <div class="detail-label">
                            Name
                        </div>

                        <div class="detail-value">
                            {approver_name}
                        </div>

                    </div>


                    <div class="detail-row">

                        <div class="detail-label">
                            Employee ID
                        </div>

                        <div class="detail-value">
                            {approver_employee_id}
                        </div>

                    </div>


                    <div class="detail-row">

                        <div class="detail-label">
                            Email
                        </div>

                        <div class="detail-value">
                            {approver_email}
                        </div>

                    </div>


                    <div class="detail-row">

                        <div class="detail-label">
                            Status
                        </div>

                        <div class="detail-value">
                            <strong>
                                {status_text}
                            </strong>
                        </div>

                    </div>

                </div>

            </div>


            <!-- Approver Message -->

            <div class="section">

                <h3 class="section-title">
                    Message from Approver
                </h3>

                <div class="approver-message">
                    {approver_message}
                </div>

            </div>

        </div>


        <!-- Footer -->

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
    # ============================================
    # Send Email
    # ============================================

    try:

        response = resend.Emails.send({
            "from": RESEND_FROM_EMAIL,
            "to": [requestor_email],
            "subject": subject,
            "html": html,
        })

        return {
            "success": True,
            "message": "Requestor email sent successfully",
            "response": response
        }

    except Exception as e:

        print(
            f"Failed to send requestor email: {e}"
        )

        return {
            "success": False,
            "message": "Failed to send requestor email",
            "error": str(e)
        }