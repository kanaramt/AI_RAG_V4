from enum import Enum


class ReviewStatus(str, Enum):
    """
    Enterprise Knowledge Review Status.
    """

    PENDING = "pending"

    IN_REVIEW = "in_review"

    APPROVED = "approved"

    REJECTED = "rejected"

    COMPLETED = "completed"

    FAILED = "failed"

    ARCHIVED = "archived"
