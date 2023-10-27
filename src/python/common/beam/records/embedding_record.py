from pydantic import BaseModel


class TitleEmbedding(BaseModel):
    paper_id: str
    embeddings: list[float]


class ClaimEmbedding(BaseModel):
    claim_id: str
    paper_id: str
    sentence_id: int
    embeddings: list[float]
