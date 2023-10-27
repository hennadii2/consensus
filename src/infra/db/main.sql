-- Primary table for all ingested paper metadata
CREATE TABLE papers (
  id BIGSERIAL PRIMARY KEY,
  -- gcs blob storage location of the raw paper data
  raw_data_url TEXT NOT NULL,
  -- gcs blob store location of the clean paper data
  -- null if data was not yet cleaned (eg. unsupported language)
  clean_data_url TEXT,
  clean_data_hash TEXT,
  -- [DEPRECATED] src/protos/paper.proto:PaperStatus schema
  status JSONB NOT NULL,
  -- src/protos/paper_metadata.proto:PaperMetadata schema
  metadata JSONB NOT NULL,
  -- provider supplied metadata, format is dependent on provider type
  provider_metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL,
  last_updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX ON papers ((metadata->>'provider_id'));

-- Primary table for all paper record versions
CREATE TABLE IF NOT EXISTS paper_records (
  row_id BIGSERIAL PRIMARY KEY,
  paper_id TEXT NOT NULL,
  -- src/protos/paper_metadata.proto:PaperMetadata schema
  metadata JSONB NOT NULL,
  status TEXT NOT NULL,
  status_msg TEXT,
  data_hash JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  created_by TEXT NOT NULL,
  version TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS
paper_records_by_paper_id_idx ON paper_records (paper_id);

-- Primary table for all abstract record versions
CREATE TABLE IF NOT EXISTS abstract_records (
  row_id BIGSERIAL PRIMARY KEY,
  paper_id TEXT NOT NULL,
  -- location in GCS for the abstract text
  gcs_abstract_url TEXT NOT NULL,
  status TEXT NOT NULL,
  status_msg TEXT,
  data_hash JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  created_by TEXT NOT NULL,
  version TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS
abstract_records_by_paper_id_idx ON abstract_records (paper_id);

-- Primary table for all paper abstract takeaways
CREATE TABLE IF NOT EXISTS abstract_takeaways (
  row_id BIGSERIAL PRIMARY KEY,
  paper_id TEXT NOT NULL,
  takeaway TEXT NOT NULL,
  metrics JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  created_by TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS
abstract_takeaways_by_paper_id_idx ON abstract_takeaways (paper_id);

-- Primary table for all mappings from claim ID to their paper ID
CREATE TABLE IF NOT EXISTS claim_ids_to_paper_ids (
  row_id BIGSERIAL PRIMARY KEY,
  claim_id TEXT NOT NULL,
  paper_id TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  created_by TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS
claim_ids_to_paper_ids_by_claim_id_idx ON claim_ids_to_paper_ids (claim_id);

-- Primary table for all mappings from paper_id to their hash_paper_id
-- See https://consensus-app.atlassian.net/l/cp/RwN1GScB for details
CREATE TABLE IF NOT EXISTS hash_paper_ids (
  paper_id TEXT PRIMARY KEY,
  hash_paper_id TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL,
  created_by TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS
hash_paper_ids_by_hash_paper_id_idx ON hash_paper_ids (hash_paper_id);

-- Primary table for all journal data
CREATE TABLE journals (
  id BIGSERIAL PRIMARY KEY,
  -- formatted name of the journal
  name TEXT NOT NULL UNIQUE,
  -- normalized and hashed name of the journal for matching
  name_hash TEXT NOT NULL UNIQUE,
  -- print ISSN, null if unavailable
  print_issn TEXT,
  -- electrionic ISSN, null if unavailable
  electronic_issn TEXT,
  created_at TIMESTAMPTZ NOT NULL,
  created_by TEXT NOT NULL,
  last_updated_at TIMESTAMPTZ NOT NULL,
  last_updated_by TEXT NOT NULL
);

CREATE INDEX ON journals (name_hash);

-- Primary table for all journal scores
CREATE TABLE journal_scores (
  id BIGSERIAL PRIMARY KEY,
  -- same ID as journals table
  journal_id BIGINT NOT NULL,
  -- year this score is relevant to
  year SMALLINT NOT NULL,
  -- src/protos/journal.proto:ScoreProvider enum
  provider TEXT NOT NULL,
  -- src/protos/journal.proto:*ScoreMetadata type based on provider field
  metadata JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  created_by TEXT NOT NULL
);

CREATE INDEX ON journal_scores (journal_id, year, provider);

-- Primary table for all journal scores
CREATE TABLE paper_inferences (
  id BIGSERIAL PRIMARY KEY,
  -- same ID as papers table
  paper_id BIGINT NOT NULL,
  -- src/protos/paper_inferences.proto:InferenceType enum
  type TEXT NOT NULL,
  -- src/protos/paper_inferences.proto:InferenceProvider enum
  provider TEXT NOT NULL,
  -- location of source for the inference (eg. GCS directory of output)
  source TEXT NOT NULL,
  -- src/protos/paper_inferences.proto:InferenceData
  data JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  created_by TEXT NOT NULL
);

CREATE INDEX ON paper_inferences (paper_id, type);

-- Primary table for all stripe subscription products
CREATE TABLE IF NOT EXISTS subscription_products (
  id BIGSERIAL PRIMARY KEY,
  stripe_product_id TEXT NOT NULL,
  stripe_json_data TEXT NOT NULL,
  version_created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX ON subscription_products (stripe_product_id);
CREATE INDEX ON subscription_products (version_created_at);

-- Primary table for all customer subscriptions
CREATE TABLE IF NOT EXISTS customer_subscriptions (
  id BIGSERIAL PRIMARY KEY,
  stripe_customer_id TEXT,
  stripe_json_data TEXT,
  version_created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX ON customer_subscriptions (stripe_customer_id);

-- Primary table for all bookmark lists
CREATE TABLE IF NOT EXISTS bookmark_lists (
  id TEXT PRIMARY KEY,
  clerk_user_id TEXT NOT NULL,
  text_label TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  deleted_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS
bookmark_lists_by_clerk_user_id ON bookmark_lists (clerk_user_id);

-- Primary table for all bookmark list items
CREATE TYPE bookmark_type AS ENUM ('paper', 'search');
CREATE TABLE IF NOT EXISTS bookmark_items (
  id BIGSERIAL PRIMARY KEY,
  clerk_user_id TEXT NOT NULL,
  bookmark_list_id TEXT NOT NULL REFERENCES bookmark_lists(id),
  bookmark_type bookmark_type NOT NULL,
  claim_id TEXT,
  paper_id TEXT,
  search_url TEXT,
  created_at TIMESTAMPTZ NOT NULL,
  deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS
bookmarks_by_clerk_user_id ON bookmark_items (clerk_user_id);
CREATE INDEX IF NOT EXISTS
bookmarks_by_bookmark_list_id ON bookmark_items (bookmark_list_id);
