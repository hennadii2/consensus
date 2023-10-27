from dataclasses import dataclass

from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384


@dataclass(frozen=True)
class SimilaritySearchEmbeddingModel:
    model: SentenceTransformer
    embedding_dimensions: int


def initialize_similarity_search_embedding_model() -> SimilaritySearchEmbeddingModel:
    """
    Returns a model to use with initial vector similarity search.
    """
    transformer = SentenceTransformer(MODEL_NAME)
    return SimilaritySearchEmbeddingModel(
        model=transformer,
        embedding_dimensions=EMBEDDING_DIMENSIONS,
    )


def encode_similarity_search_embedding(
    model: SimilaritySearchEmbeddingModel,
    text: str,
) -> list[float]:
    """
    Returns an embedding for text that can be used in vector similarity search.
    """
    embeddings = model.model.encode(text, normalize_embeddings=True)
    float_embeddings = list(map(float, embeddings))
    if len(float_embeddings) != model.embedding_dimensions:
        raise ValueError(
            f"""
        Unexpected embedding dimensions.
        Excepted {model.embedding_dimensions} found {len(float_embeddings)}.
        """
        )
    return float_embeddings
