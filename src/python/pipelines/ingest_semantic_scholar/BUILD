python_sources()

pex_binary(
    name="ingest_semantic_scholar_main",
    entry_point="main.py",
)

python_distribution(
    name="ingest_semantic_scholar_dist",
    dependencies=[
        ":ingest_semantic_scholar",
    ],
    provides=python_artifact(
        name="ingest_semantic_scholar_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="ingest_semantic_scholar_runner",
    dependencies=[
        ":ingest_semantic_scholar",
        ":ingest_semantic_scholar_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
