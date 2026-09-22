from schemas.versioning.document_version import (
    DocumentVersion,
)


class VersionRepository:
    """
    Temporary in-memory repository.

    Future:
    PostgreSQL
    """

    def __init__(self):

        self._versions: list[DocumentVersion] = []

    def create(
        self,
        version: DocumentVersion,
    ) -> DocumentVersion:

        self._versions.append(version)

        return version

    def get_all(
        self,
    ) -> list[DocumentVersion]:

        return self._versions

    def get_document_versions(
        self,
        document_id: str,
    ) -> list[DocumentVersion]:

        return [
            version
            for version in self._versions
            if version.document_id == document_id
        ]

    def get_latest(
        self,
        document_id: str,
    ) -> DocumentVersion | None:

        versions = self.get_document_versions(
            document_id
        )

        if not versions:
            return None

        return max(
            versions,
            key=lambda version: version.version_number,
        )
