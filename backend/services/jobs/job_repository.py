from schemas.jobs.job import Job, JobStatus


class JobRepository:
    """
    Temporary in-memory repository.

    Future:
    PostgreSQL
    """

    def __init__(self):

        self._jobs: list[Job] = []

    def create(
        self,
        job: Job,
    ) -> Job:

        self._jobs.append(job)

        return job

    def get_all(
        self,
    ) -> list[Job]:

        return self._jobs

    def get(
        self,
        job_id: str,
    ) -> Job | None:

        for job in self._jobs:

            if job.job_id == job_id:

                return job

        return None

    def update(
        self,
        job_id: str,
        status: JobStatus,
        progress: int,
        message: str,
    ) -> bool:

        job = self.get(job_id)

        if job is None:
            return False

        job.status = status
        job.progress = progress
        job.message = message

        return True
