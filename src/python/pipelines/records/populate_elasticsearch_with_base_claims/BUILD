python_sources()

pex_binary(
    name="populate_elasticsearch_with_base_claims_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#pip",
    ]
)

python_distribution(
    name="populate_elasticsearch_with_base_claims_dist",
    dependencies=[
        ":populate_elasticsearch_with_base_claims",
        "//3rdparty/python#pip",
    ],
    provides=python_artifact(
        name="populate_elasticsearch_with_base_claims_dist",
        version="1.0",
    ),
)

docker_image(
    name="populate_elasticsearch_with_base_claims_runner",
    dependencies=[
        ":populate_elasticsearch_with_base_claims",
        ":populate_elasticsearch_with_base_claims_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
