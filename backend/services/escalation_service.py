from datetime import datetime

from sqlmodel import Session, select

from database.database import engine
from models.request_model import RequestModel
from constants.status import RequestStatus

from utility.sendEscalationEmail import (
    send_escalation_email
)


def process_escalations():

    try:

        with Session(engine) as session:

            now = datetime.now()

            # ========================================
            # Find requests whose deadline has passed
            # ========================================

            requests = session.exec(
                select(RequestModel)
                .where(
                    RequestModel.status
                    == RequestStatus.APPROVAL_PENDING,

                    RequestModel.reply_deadline
                    <= now
                )
            ).all()

            # ========================================
            # Process each request
            # ========================================

            for request in requests:

                # ====================================
                # Make sure senior manager exists
                # ====================================

                if (
                    request.senior_manager_employee_id
                    is None
                    or request.senior_manager_name
                    is None
                    or request.senior_manager_email
                    is None
                ):

                    print(
                        "Cannot escalate request "
                        f"{request.tracking_id}: "
                        "Senior manager details missing."
                    )

                    continue

                # ====================================
                # Store senior manager details
                # before changing approver
                # ====================================

                senior_manager_name = (
                    request.senior_manager_name
                )

                senior_manager_employee_id = (
                    request.senior_manager_employee_id
                )

                senior_manager_email = (
                    request.senior_manager_email
                )

                # ====================================
                # Determine request message
                # ====================================

                request_message = (
                    request.clarified_requestor_message
                    if request.clarified_requestor_message
                    else request.requestor_message
                )

                # ====================================
                # Change approver to senior manager
                # ====================================

                request.approver_employee_id = (
                    senior_manager_employee_id
                )

                request.approver_name = (
                    senior_manager_name
                )

                request.approver_email = (
                    senior_manager_email
                )

                # ====================================
                # Update status
                # ====================================

                request.status = (
                    RequestStatus.ESCALATED
                )

                # ====================================
                # Send escalation email
                # ====================================

                try:

                    email_result = send_escalation_email(

                        senior_manager_name=(
                            senior_manager_name
                        ),

                        senior_manager_employee_id=(
                            senior_manager_employee_id
                        ),

                        senior_manager_email=(
                            senior_manager_email
                        ),

                        requestor_message=(
                            request_message
                        ),

                        requestor_email=(
                            request.requestor_email
                        ),

                        tracking_id=(
                            request.tracking_id
                        ),

                        priority=(
                            request.priority
                        ),

                        reply_within=(
                            request.reply_within
                        )
                    )

                    print(
                        "Escalation Email Result:"
                    )

                    print(email_result)

                    # ====================================
                    # Clear reply deadline
                    #
                    # Email was sent successfully
                    # so this request should no longer
                    # be considered for escalation.
                    # ====================================

                    if (
                        email_result
                        and email_result.get("success")
                    ):

                        request.reply_within = None

                    else:

                        print(
                            "Escalation email was not "
                            "sent successfully for "
                            f"{request.tracking_id}"
                        )

                except Exception as email_error:

                    print(
                        "Failed to send escalation "
                        f"email for "
                        f"{request.tracking_id}: "
                        f"{email_error}"
                    )

                # ====================================
                # Save database changes
                # ====================================

                session.add(request)

                session.commit()

                session.refresh(request)

                print(
                    f"Request {request.tracking_id} "
                    f"has been escalated to "
                    f"{request.approver_name}"
                )

    except Exception as e:

        print(
            "Escalation service error:",
            e
        )