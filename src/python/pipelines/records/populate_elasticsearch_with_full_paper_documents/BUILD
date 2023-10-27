python_sources()

pex_binary(
    name="populate_elasticsearch_with_full_paper_documents_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#pip",
        "//3rdparty/python#setuptools",
    ],
    # Enable this to run locally on M1/M2 Macs
    # environment="py39_local_arm64",
)

python_distribution(
    name="populate_elasticsearch_with_full_paper_documents_dist",
    dependencies=[
        ":populate_elasticsearch_with_full_paper_documents",
        "//3rdparty/python#pip",
    ],
    provides=python_artifact(
        name="populate_elasticsearch_with_full_paper_documents_dist",
        version="1.0",
    ),
)

docker_image(
    name="populate_elasticsearch_with_full_paper_documents_runner",
    dependencies=[
        ":populate_elasticsearch_with_full_paper_documents",
        ":populate_elasticsearch_with_full_paper_documents_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
