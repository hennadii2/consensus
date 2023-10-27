from functools import partial
from typing import Callable, Optional, cast

import redis
from common.cache.cache_util import Cache, read_from_cache, write_to_cache
from common.models.question_answer_ranker import MODEL_VERSION_SEARCH_RANKER
from web.backend.app.common.disputed import DisputedData
from web.chat_gpt_plugin.app.endpoints.search.data import DETAILS_BASE_URL, SearchResponse


def init_cache(
    full_url: str,
    query: str,
    disputed: DisputedData,
) -> Optional[Cache[SearchResponse]]:
    """Search endpoint response cache"""
    dependent_models = f"{MODEL_VERSION_SEARCH_RANKER}"  # noqa: E501

    cache_key = f"chat_gpt_plugin_search:{full_url}:{query}:{dependent_models}:{disputed.version}:4"  # noqa: E501
    read = cast(
        Callable[[redis.Redis], Optional[SearchResponse]],
        partial(read_from_cache, cache_key, SearchResponse),
    )
    write = partial(write_to_cache, cache_key)
    return Cache[SearchResponse](read=read, write=write)


def make_details_url(claim_id: str, url_slug: str) -> str:
    return f"{DETAILS_BASE_URL}/{url_slug}/{claim_id}/?utm_source=chatgpt"
