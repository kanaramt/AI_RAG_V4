import numpy as np


class Similarity:
    """
    Utility class for similarity calculations.
    """

    @staticmethod
    def cosine_similarity(
        embedding1: list[float],
        embedding2: list[float],
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        """

        vec1 = np.array(embedding1, dtype=float)
        vec2 = np.array(embedding2, dtype=float)

        denominator = (
            np.linalg.norm(vec1)
            * np.linalg.norm(vec2)
        )

        if denominator == 0:
            return 0.0

        similarity = np.dot(vec1, vec2) / denominator

        return float(similarity)
