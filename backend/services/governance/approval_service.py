import uuid
from datetime import datetime

from schemas.governance.approval import (
    ApprovalRequest,
    ApprovalStatus,
)
from utils.datetime_utils import ist_now

class ApprovalService:
    """
    Enterprise Approval Workflow Service.
    """

    def __init__(self):

        self._requests: list[ApprovalRequest] = []

    def create(
        self,
        resource_type: str,
        resource_id: str,
        requested_by: str,
        assigned_to: str,
    ) -> ApprovalRequest:

        request = ApprovalRequest(

            approval_id=str(uuid.uuid4()),

            resource_type=resource_type,

            resource_id=resource_id,

            requested_by=requested_by,

            assigned_to=assigned_to,
        )

        self._requests.append(request)

        return request

    def get_all(
        self,
    ) -> list[ApprovalRequest]:

        return self._requests

    def update_status(
        self,
        approval_id: str,
        status: ApprovalStatus,
        comments: str = "",
    ) -> bool:

        for request in self._requests:

            if request.approval_id == approval_id:

                request.status = status

                request.comments = comments

                request.updated_at = ist_now()

                return True

        return False
