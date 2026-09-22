"""
Enterprise Knowledge Feedback Service
"""

from schemas.feedback.knowledge_feedback import (
    KnowledgeFeedback,
)


class FeedbackService:
    """
    Handles all knowledge feedback events.

    Current Version
    ---------------
    ✓ Accept feedback
    ✓ Validate feedback
    ✓ Log feedback

    Future Versions
    ---------------
    ✓ Store in database
    ✓ Trigger recommendation engine
    ✓ Detect duplicate reports
    ✓ Aggregate statistics
    """

    def submit(
        self,
        feedback: KnowledgeFeedback,
    ) -> bool:

        print("=" * 60)
        print("Knowledge Feedback Received")
        print("=" * 60)

        print(feedback.model_dump())

        print("=" * 60)

        return True
