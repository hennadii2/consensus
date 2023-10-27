python_sources()

pex_binary(
    name="ingestion_main",
    entry_point="main.py",
)

python_distribution(
    name="ingestion_dist",
    dependencies=[
        ":ingestion",
    ],
    provides=python_artifact(
        name="ingestion_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="ingestion_runner",
    dependencies=[
        ":ingestion",
        ":ingestion_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
