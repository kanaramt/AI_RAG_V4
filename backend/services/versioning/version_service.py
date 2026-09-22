import uuid
from datetime import datetime

from backend.schemas.versioning.document_version import (
    DocumentVersion,
    VersionStatus,
)
from backend.services.versioning.version_repository import (
    VersionRepository,
)
from backend.utils.datetime_utils import ist_now

class VersionService:
    """
    Enterprise Document Version Service.
    """

    def __init__(self):

        self.repository = VersionRepository()

    def create_version(
        self,
        document_id: str,
        created_by: str = "system",
        change_summary: str = "",
    ) -> DocumentVersion:

        latest = self.repository.get_latest(
            document_id
        )

        version_number = (
            latest.version_number + 1
            if latest
            else 1
        )

        version = DocumentVersion(

            version_id=str(uuid.uuid4()),

            document_id=document_id,

            version_number=version_number,

            status=VersionStatus.DRAFT,

            created_by=created_by,

            change_summary=change_summary,
        )

        return self.repository.create(version)

    def activate_version(
        self,
        version_id: str,
    ) -> bool:

        for version in self.repository.get_all():

            if version.version_id == version_id:

                version.status = VersionStatus.ACTIVE

                version.activated_at = ist_now()

                return True

        return False

    def get_versions(
        self,
        document_id: str,
    ) -> list[DocumentVersion]:

        return self.repository.get_document_versions(
            document_id
        )

    def get_latest(
        self,
        document_id: str,
    ) -> DocumentVersion | None:

        return self.repository.get_latest(
            document_id
        )