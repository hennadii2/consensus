from fastapi import APIRouter
from web.backend.app.endpoints.add_stripe_subscription.endpoint import router as add_stripe_sub
from web.backend.app.endpoints.autocomplete import router as autocomplete
from web.backend.app.endpoints.bookmarks.items.endpoint import router as bookmark_items
from web.backend.app.endpoints.bookmarks.lists.endpoints import router as bookmark_lists
from web.backend.app.endpoints.claims.details.endpoint import router as claim_details_router
from web.backend.app.endpoints.delete_stripe_subscription.endpoint import (
    router as delete_stripe_sub,
)
from web.backend.app.endpoints.get_stripe_subscription.endpoint import router as get_stripe_sub
from web.backend.app.endpoints.healthcheck.endpoint import router as healthcheck_router
from web.backend.app.endpoints.paper_search.endpoint import router as paper_search_router
from web.backend.app.endpoints.papers.details.endpoint import router as paper_details_router
from web.backend.app.endpoints.search.endpoint import router as search_router
from web.backend.app.endpoints.sitemap import router as sitemap_router
from web.backend.app.endpoints.study_details.endpoint import router as study_details
from web.backend.app.endpoints.subscription_products.endpoint import router as sub_products
from web.backend.app.endpoints.summary.endpoint import router as summary
from web.backend.app.endpoints.trending import router as trending_router
from web.backend.app.endpoints.yes_no.endpoint import router as yes_no

router = APIRouter()

router.include_router(healthcheck_router, tags=["healthcheck"])
router.include_router(sitemap_router, tags=["sitemap"])
router.include_router(search_router, prefix="/search", tags=["search"])
router.include_router(paper_search_router, prefix="/paper_search", tags=["paper_search"])
router.include_router(claim_details_router, prefix="/claims/details", tags=["claim_details"])
router.include_router(paper_details_router, prefix="/papers/details", tags=["paper_details"])
router.include_router(trending_router, prefix="/trending", tags=["trending"])
router.include_router(yes_no, prefix="/yes_no", tags=["yes_no"])
router.include_router(summary, prefix="/summary", tags=["summary"])
router.include_router(study_details, prefix="/study_details", tags=["study_details"])
router.include_router(autocomplete, prefix="/autocomplete", tags=["autocomplete"])
router.include_router(sub_products, prefix="/subscription_products", tags=["sub_product"])
router.include_router(add_stripe_sub, prefix="/add_stripe_subscription", tags=["add_stripe_sub"])
router.include_router(get_stripe_sub, prefix="/get_stripe_subscription", tags=["get_stripe_sub"])
router.include_router(
    delete_stripe_sub, prefix="/delete_stripe_subscription", tags=["delete_stripe_sub"]
)
router.include_router(bookmark_items, prefix="/bookmarks/items", tags=["bookmark_items"])
router.include_router(bookmark_lists, prefix="/bookmarks/lists", tags=["bookmark_lists"])
