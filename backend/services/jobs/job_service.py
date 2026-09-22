import uuid

from schemas.jobs.job import (
    Job,
    JobStatus,
    JobType,
)
from services.jobs.job_repository import (
    JobRepository,
)


class JobService:
    """
    Enterprise Job Service.
    """

    def __init__(self):

        self.repository = JobRepository()

    def create_job(
        self,
        job_type: JobType,
        created_by: str = "system",
        message: str = "",
    ) -> Job:

        job = Job(

            job_id=str(uuid.uuid4()),

            job_type=job_type,

            created_by=created_by,

            message=message,
        )

        return self.repository.create(job)

    def get_jobs(
        self,
    ) -> list[Job]:

        return self.repository.get_all()

    def get_job(
        self,
        job_id: str,
    ) -> Job | None:

        return self.repository.get(job_id)

    def update_job(
        self,
        job_id: str,
        status: JobStatus,
        progress: int,
        message: str,
    ) -> bool:

        return self.repository.update(
            job_id,
            status,
            progress,
            message,
        )
