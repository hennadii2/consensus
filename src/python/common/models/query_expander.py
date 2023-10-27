from dataclasses import dataclass

from gensim.models import KeyedVectors  # type: ignore
from huggingface_hub import login, snapshot_download  # type: ignore
from nltk import download as nltk_download
from nltk.corpus import stopwords as nltk_stopwords
from nltk.tokenize import word_tokenize  # type: ignore

_HUGGING_FACE_QUERY_EXPANSION_REPO = "Consensus/Word2Vec"
_WORD_2_VEC_VECTORS_PATH = "word2vec.wordvectors"

MODEL_VERSION_QUERY_EXPANDER = (
    f"{_HUGGING_FACE_QUERY_EXPANSION_REPO}:{_WORD_2_VEC_VECTORS_PATH}"  # noqa: E501
)


@dataclass(frozen=True)
class QueryExpander:
    model: KeyedVectors


def initialize_query_expander(hf_access_token: str) -> QueryExpander:
    """
    Returns a model and tokenizer to use with the question classifier.
    """
    nltk_download("stopwords")
    nltk_download("punkt")

    login(token=hf_access_token)
    repo_path = snapshot_download(repo_id=_HUGGING_FACE_QUERY_EXPANSION_REPO)
    model = KeyedVectors.load(f"{repo_path}/{_WORD_2_VEC_VECTORS_PATH}", mmap="r")
    return QueryExpander(model=model)


def expand_query(
    expander: QueryExpander,
    query: str,
) -> str:
    """
    Returns a modified query with synonyms expanded.
    """

    query = query.lower()
    tokens = word_tokenize(query)
    stopwords = nltk_stopwords.words("english")

    # remove tokens that are just special characters
    # filtered_words = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in filtered_words]
    filtered_words = [word for word in tokens if word not in stopwords]
    filtered_words = [f for f in filtered_words if len(f) >= 2]
    filtered_words = [x for x in filtered_words if x]

    synonyms = []
    for token in filtered_words:
        try:
            topx = expander.model.most_similar(token, topn=5)
        except KeyError:
            continue
        synonyms.extend([w[0].lower() for w in topx if w[1] > 0.7])

    unique_synonyms = " ".join(list(set(synonyms)))
    return f"{query} {unique_synonyms}"
