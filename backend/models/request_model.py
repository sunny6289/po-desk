from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from constants.status import RequestStatus


class RequestModel(BaseModel):

    # Requestor
    requestor_id: int
    requestor_email: str
    created_at: datetime
    requestor_message: str

    # Request
    tracking_id: str
    status: RequestStatus

    # Department
    department_id: int
    department_name: str

    # Approver
    approver_employee_id: int
    approver_name: str
    approver_email: str

    # Senior Manager
    senior_manager_employee_id: Optional[int] = None
    senior_manager_name: Optional[str] = None
    senior_manager_email: Optional[str] = None

    # Clarification
    need_clarification: bool
    clarifications_required: Optional[list[str]] = None
    clarified_requestor_message: Optional[str] = None

    # Priority
    priority: Optional[str] = None

    # Approval
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None