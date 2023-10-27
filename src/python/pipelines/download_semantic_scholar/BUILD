python_sources()

pex_binary(
    name="download_semantic_scholar_main",
    entry_point="main.py",
)

python_distribution(
    name="download_semantic_scholar_dist",
    dependencies=[
        ":download_semantic_scholar",
    ],
    provides=python_artifact(
        name="download_semantic_scholar_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="download_semantic_scholar_runner",
    dependencies=[
        ":download_semantic_scholar",
        ":download_semantic_scholar_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
