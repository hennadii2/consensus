import math
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Optional, Sequence
from xml.etree import ElementTree as etree

from claim_pb2 import Claim

XML_XMLNS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ROOT_PAGE_NAME = "sitemap.xml"


@dataclass(frozen=True)
class SitemapEntry:
    sitemap: str
    text: str
    is_sitemap_index: bool


def _create_sitemap_entry(
    base_url: str, claim: Claim, current_sitemap: str, parent_sitemap: Optional[str]
) -> SitemapEntry:
    if parent_sitemap:
        sitemap_url = f"{base_url}/{parent_sitemap}"
        return SitemapEntry(
            sitemap=current_sitemap,
            text=sitemap_url,
            is_sitemap_index=True,
        )

    claim_url = f"{base_url}/details/{claim.metadata.url_slug}/{claim.id}/"
    return SitemapEntry(
        sitemap=current_sitemap,
        text=claim_url,
        is_sitemap_index=False,
    )


def generate_sitemap_entries(
    claim: Claim,
    count_id: int,
    hierarchy: list[int],
    base_url: str,
) -> Iterator[SitemapEntry]:
    """
    For a given count ID, generates an entry for each sitemap represented by an
    integer in the given hierarchy.
    """
    previous_split = count_id
    previous_page: Optional[str] = None

    for index, mod in enumerate(hierarchy):
        split = previous_split % mod
        page_name = f"sitemaps/{len(hierarchy)-index}/{split}.xml"
        yield _create_sitemap_entry(base_url, claim, page_name, previous_page)

        previous_page = page_name
        previous_split = split

    yield _create_sitemap_entry(base_url, claim, ROOT_PAGE_NAME, previous_page)


def get_sitemap_distribution_hierarchy(num_items, max_items) -> tuple[list[int], int]:
    """
    Assuming a sitemap can hold up to {max_items} number of entries, this function
    generates a list of levels that can be used to evenly distribute all {num_items}
    across files when used along with generate_sitemap_entries.
    """
    hierarchy = []
    num_leaf_level_sitemaps = math.ceil(num_items / max_items)
    parent_mod = num_leaf_level_sitemaps
    while parent_mod > 1:
        hierarchy.append(parent_mod)
        parent_mod = math.ceil(parent_mod / max_items)
    return (hierarchy, num_leaf_level_sitemaps)


def _add_sitemap_entry_xml(
    builder: etree.TreeBuilder,
    entry: str,
    date: str,
    is_sitemap_index: bool,
):
    if is_sitemap_index:
        builder.start("sitemap", {})
    else:
        builder.start("url", {})

    builder.start("loc", {})
    builder.data(entry)
    builder.end("loc")

    builder.start("lastmod", {})
    builder.data(date)
    builder.end("lastmod")

    if is_sitemap_index:
        builder.end("sitemap")
    else:
        builder.end("url")


def build_sitemap_from_entries(
    sitemap_name: str,
    entries: Sequence[SitemapEntry],
    timestamp: datetime,
    is_sitemap_index: bool,
    add_to_root_entry: list[str],
) -> etree.Element:
    """ """
    date = timestamp.strftime("%Y-%m-%d")
    builder = etree.TreeBuilder()
    if is_sitemap_index:
        builder.start("sitemapindex", {"xmlns": XML_XMLNS})
        if sitemap_name == ROOT_PAGE_NAME:
            for additional_entry in add_to_root_entry:
                _add_sitemap_entry_xml(
                    builder=builder,
                    entry=additional_entry,
                    date=date,
                    is_sitemap_index=True,
                )

        for entry in entries:
            _add_sitemap_entry_xml(
                builder=builder,
                entry=entry.text,
                date=date,
                is_sitemap_index=True,
            )
        builder.end("sitemapindex")
    else:
        builder.start("urlset", {"xmlns": XML_XMLNS})
        for entry in entries:
            _add_sitemap_entry_xml(
                builder=builder,
                entry=entry.text,
                date=date,
                is_sitemap_index=False,
            )
        builder.end("urlset")
    return builder.close()
