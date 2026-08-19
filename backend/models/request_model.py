from datetime import datetime

from sqlmodel import Field, SQLModel

from constants.status import RequestStatus


class RequestModel(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    # ============================================
    # Requestor
    # ============================================

    requestor_id: int

    requestor_email: str

    created_at: datetime

    requestor_message: str

    clarified_requestor_message: str | None = None

    # ============================================
    # Tracking
    # ============================================

    tracking_id: str = Field(
        index=True,
        unique=True
    )

    # ============================================
    # Request Status
    # ============================================

    status: RequestStatus

    # ============================================
    # Department
    # ============================================

    department_id: int

    department_name: str

    # ============================================
    # Approver
    # ============================================

    approver_employee_id: int

    approver_name: str

    approver_email: str

    # ============================================
    # Senior Manager
    # ============================================

    senior_manager_employee_id: int | None = None

    senior_manager_name: str | None = None

    senior_manager_email: str | None = None

    # ============================================
    # Clarification
    # ============================================

    need_clarification: bool

    clarifications_required: str | None = None

    # ============================================
    # Priority
    # ============================================

    priority: str | None = None

    average_probability: float | None = None

    # ============================================
    # Approval
    # ============================================

    approved_by: int | None = None

    approved_at: datetime | None = None
    approver_message: str | None = None
    reply_within: int | None = None
    reply_deadline: datetime | None = None