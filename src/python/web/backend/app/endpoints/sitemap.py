from common.storage.sitemaps import read_sitemap
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from web.backend.app.state import SharedState

router = APIRouter()


@router.get("/sitemap")
def sitemap(request: Request, path: str):
    shared: SharedState = request.app.state.shared

    path = path[1:] if path[0] == "/" else path
    sitemap = read_sitemap(
        client=shared.storage_client,
        # TODO(meganvw): Remove hard coding once we generate sitemap for new index
        search_index_id="20220928180152-claim_extraction_biomed_roberta_v1_0-purpose_fix-claims-221223203652-shrunk",  # noqa: E501
        # search_index_id=shared.config.search_index_id,
        sitemap_path=path,
    )
    if sitemap:
        return Response(content=sitemap, media_type="text/xml")
    else:
        raise HTTPException(status_code=404, detail="Sitemap not found")
