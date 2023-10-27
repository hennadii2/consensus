from enum import Enum

from pydantic import BaseModel, Field

DETAILS_BASE_URL = "https://consensus.app/details"
ENDPOINT_SUMMARY = "Returns answers to a question for research papers, with each result containing the claim, title, authors, year, and journal."  # noqa: E501
ENDPOINT_DESCRIPTION = "An endpoint that can be called to ask a question of research papers"

LOG_ENDPOINT = "chat_gpt_plugin_search"


class LOG_EVENTS(Enum):
    LOAD_FROM_CACHE = "load_from_cache"
    FULL_SEARCH = "full_search"


class SearchRequest(BaseModel):
    query: str = Field(
        description="A question to ask against research papers. To use the Consensus search engine effectively, ask research-oriented questions related to scientific topics that have likely been studied, such as the impact of climate change on GDP or the benefits of mindfulness meditation. Avoid basic factual queries and instead ask yes/no questions, inquire about the relationship between concepts, or ask about the effects, impact, or benefits of a concept. Rephrase queries as simple questions, such as 'What is the effect of X on Y?' or 'Does X lead to Y?'. When asking a complex query, break it down into multiple questions. For example, instead of asking 'What is the effect of X on Y and Z?', ask 'What is the effect of X on Y?' and 'What is the effect of X on Z?' To ensure proper citation, please cite the authors of each paper when listing claims about them. For example, 'X is shown to lead to Y. [Author1 et al., 2021]']"  # noqa: E501
    )


class SearchResponseItem(BaseModel):
    claim_text: str = Field(description="An answer to the query.")
    paper_title: str = Field(description="Title of the paper where the answer was found")
    paper_authors: list[str] = Field(description="A list of authors of the paper.")
    paper_publish_year: int = Field(description="The year the paper was published.")
    publication_journal_name: str = Field(description="The journal the paper was published in.")
    consensus_paper_details_url: str = Field(description="A URL with more details on the paper.")
    doi: str = Field(
        description="Digital Object Identifier, a unique alphanumeric string assigned to a document for permanent access."  # noqa: E501
    )
    volume: str = Field(description="The volume of the journal in which the paper appears.")
    pages: str = Field(description="The page range of the paper within the journal volume.")


class SearchResponse(BaseModel):
    items: list[SearchResponseItem] = Field(description="All answers to the question.")
