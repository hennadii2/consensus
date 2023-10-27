python_sources()

pex_binary(
    name="update_elasticsearch_with_title_embeddings_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#pip",
    ]
)

python_distribution(
    name="update_elasticsearch_with_title_embeddings_dist",
    dependencies=[
        ":update_elasticsearch_with_title_embeddings",
        "//3rdparty/python#pip",
    ],
    provides=python_artifact(
        name="update_elasticsearch_with_title_embeddings_dist",
        version="1.0",
    ),
)

docker_image(
    name="update_elasticsearch_with_title_embeddings_runner",
    dependencies=[
        ":update_elasticsearch_with_title_embeddings",
        ":update_elasticsearch_with_title_embeddings_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
