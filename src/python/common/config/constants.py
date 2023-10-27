"""
Common constants used across the project.
"""

# Base URL for the production website
PROD_URL = "https://consensus.app"
PROD_URL_WORDPRESS_SITEMAP = "https://consensus.app/home/sitemap_index.xml"

# Repo relative path of environment variable file for local web backend.
REPO_PATH_LOCAL_DOT_ENV = "src/python/web/.env.local"
# Repo relative path of environment variable file production deployment file.
REPO_PATH_WEB_BACKEND_PROD_DEPLOYMENT = "src/python/web/backend/appengine_production.yaml"

# Repo relative path of semantic scholar mock data.
REPO_PATH_MOCK_DATA_SEMANTIC_SCHOLAR = (
    "src/mock_data/raw_semantic_scholar_s2-corpus-000_2022-01-01.gz"
)
# Repo relative path of autocomplete mock data.
REPO_PATH_MOCK_DATA_AUTOCOMPLETE_QUERIES = (
    "src/mock_data/autocomplete_queries_generated_questions_openai.csv"
)
# Repo relative path of root data directory.
REPO_PATH_DATA = "data"
REPO_PATH_WEB_DATA_QUERIES_JSON = f"{REPO_PATH_DATA}/web/example_queries.json"
REPO_PATH_WEB_DATA_DISPUTED_JSON = f"{REPO_PATH_DATA}/web/disputed_results.json"

# Repo relative path of main database SQL definitions.
REPO_PATH_MAIN_SQL = "src/infra/db/main.sql"

# Cloud storage bucket for pipeline log output.
BUCKET_NAME_PIPELINE_LOGS = "consensus-pipeline-logs"

# Cloud storage bucket for paper data, datasets, and model output.
BUCKET_NAME_PAPER_DATA = "consensus-paper-data"
BUCKET_NAME_PAPER_DATA_DEV = "consensus-paper-data-dev"
BUCKET_NAME_WEB_DATA = "consensus-web-data"
BUCKET_NAME_WEB_DATA_DEV = "consensus-web-data-dev"
