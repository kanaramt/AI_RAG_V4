import time

from schemas.jobs.job import (
    Job,
    JobStatus,
    JobType,
)
from services.jobs.job_service import (
    JobService,
)


class JobRunner:
    """
    Enterprise Job Runner.

    Responsible for executing long-running jobs.

    Future
    ------
    - Async execution
    - Celery
    - Redis Queue
    - Kafka
    - RabbitMQ
    - Distributed workers
    """

    def __init__(self):

        self.job_service = JobService()

    def run(
        self,
        job: Job,
    ) -> Job:

        self.job_service.update_job(
            job.job_id,
            JobStatus.RUNNING,
            0,
            "Job started.",
        )

        for progress in range(10, 101, 10):

            time.sleep(0.2)

            self.job_service.update_job(
                job.job_id,
                JobStatus.RUNNING,
                progress,
                f"{progress}% completed",
            )

        self.job_service.update_job(
            job.job_id,
            JobStatus.COMPLETED,
            100,
            "Job completed successfully.",
        )

        return self.job_service.get_job(
            job.job_id
        )
