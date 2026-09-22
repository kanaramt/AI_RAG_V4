from anthropic.types.beta import beta_managed_agents_agent_tool_config
from anthropic.types.beta import beta_managed_agents_agent_tool_config
from anthropic.types.beta import beta_managed_agents_agent_tool_config
from conda.core import index
from tests.test_chunk_validator import chunks
from services.chunking.base_chunker import BaseChunker
from services.chunking.sentence_splitter import SentenceSplitter
from services.chunking.similarity import Similarity
from services.embeddings.embedding_factory import EmbeddingFactory
from services.chunking.chunk_validator import ChunkValidator
from models.chunk import Chunk


class SemanticChunker(BaseChunker):
    """
    Production-grade semantic chunker.

    Pipeline:
    1. Split into sentences
    2. Generate embeddings
    3. Calculate similarities
    4. Detect topic boundaries
    5. Build semantic chunks
    """

    def __init__(
        self,
        similarity_threshold: float = 0.80,
        min_sentences: int = 2,
        max_sentences: int = 8,
        ):
        self.threshold = similarity_threshold
        self.min_sentences = min_sentences
        self.max_sentences = max_sentences

        self.validator = ChunkValidator(
            min_sentences=min_sentences,
            max_sentences=max_sentences,
        )

        self.splitter = SentenceSplitter()
        self.embedding = EmbeddingFactory.create()
        self.similarity = Similarity()

    def chunk(
        self,
        text: str,
    ) -> list[str]:

        sentences = self.splitter.split(text)

        if not sentences:
            return []

        embeddings = self.embedding.generate_embeddings(
            sentences
        )

        boundaries = []

        print("\nSimilarity Scores\n")

        for i in range(len(sentences) - 1):

            similarity = self.similarity.cosine_similarity(
                embeddings[i],
                embeddings[i + 1],
            )

            print(
                f"Sentence {i + 1} -> Sentence {i + 2}: "
                f"{similarity:.4f}"
            )

            if similarity < self.threshold:
                boundaries.append(i + 1)

        print("\nTopic Boundaries\n")

        if boundaries:
            for boundary in boundaries:
                print(
                    f"New Chunk starts at Sentence {boundary + 1}"
                )
        else:
            print("No topic changes detected.")

        chunks = []
        start = 0

        for boundary in boundaries:

            chunk = " ".join(
                sentences[start:boundary]
                )

            chunks.append(chunk)

            start = boundary

        chunks.append(
            " ".join(sentences[start:])
            )

        chunks.append(" ".join(sentences[start:]))

        chunk_objects = []

        for index, chunk_text in enumerate(chunks):
            sentence_count = len(
                self.sentence_splitter.split(chunk_text)
            )

        chunk_objects.append(
            Chunk(
                text=chunk_text,
                chunk_id=f"chunk_{index + 1}",
                sentence_count=sentence_count,
            )
        )

        return self.validator.validate(chunk_objects)

    
