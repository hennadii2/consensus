from common.search.claim_index import ClaimIndex
from common.search.connect import ElasticClient, SearchEnv
from elasticsearch.helpers import scan


def query(claim_index):
    for result in scan(
        client=claim_index.es,
        index=claim_index.name,
        query={"query": {"ids": {"values": [1, 2, 3]}}},
        scroll="1m",
        raise_on_error=False,
        script_fields={
            "embedding": {
                "script": {
                    "source": "doc['embedding'].size() > 0 ? doc['embedding'].vectorValue : null"
                }
            }
        },
        # size=self.MAX_SCROLL_SIZE,
    ):
        doc_id = result["_id"]
        embedding_dict = {
            "embedding": result["fields"]["embedding"][0],
        }
        yield (doc_id, None if None in embedding_dict.values() else embedding_dict)


def main(argv=None):
    search_env = SearchEnv("dev")
    search = ElasticClient(search_env)
    claim_index = ClaimIndex(search, "cvarano-source-mapping-test-05")

    for result in query(claim_index):
        print(result)


if __name__ == "__main__":
    main()
