from fastapi import APIRouter, HTTPException

from schemas.jobs.job import (
    JobStatus,
    JobType,
)
from services.jobs.job_service import (
    JobService,
)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)

job_service = JobService()


@router.post("/{job_type}")
async def create_job(
    job_type: JobType,
):
    return job_service.create_job(job_type)


@router.get("/")
async def get_jobs():
    return job_service.get_jobs()


@router.get("/{job_id}")
async def get_job(
    job_id: str,
):
    job = job_service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return job


@router.put("/{job_id}")
async def update_job(
    job_id: str,
    status: JobStatus,
    progress: int,
    message: str = "",
):
    success = job_service.update_job(
        job_id,
        status,
        progress,
        message,
    )

    return {
        "success": success,
    }
