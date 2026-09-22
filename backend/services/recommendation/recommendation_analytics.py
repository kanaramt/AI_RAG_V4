from schemas.recommendation.recommendation_result import (
    RecommendationResult,
)


class RecommendationAnalytics:
    """
    Analytics for Recommendations.
    """

    def summary(
        self,
        recommendations: list[
            RecommendationResult
        ],
    ) -> dict:

        total = len(recommendations)

        manual_review = sum(
            1
            for r in recommendations
            if r.recommendation_type
            == "manual_review"
        )

        update_chunk = sum(
            1
            for r in recommendations
            if r.recommendation_type
            == "update_chunk"
        )

        reembed = sum(
            1
            for r in recommendations
            if r.recommendation_type
            == "reembed"
        )

        avg_confidence = (
            sum(
                r.confidence
                for r in recommendations
            ) / total
            if total
            else 0.0
        )

        return {
            "total_recommendations": total,
            "manual_review": manual_review,
            "update_chunk": update_chunk,
            "reembed": reembed,
            "average_confidence": round(
                avg_confidence,
                2,
            ),
        }
