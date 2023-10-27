python_sources(
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
        "//3rdparty/python#pandas",
        "//3rdparty/python#google-apitools",
        "//3rdparty/python#openpyxl",
        "//3rdparty/python#fsspec",
        "//3rdparty/python#gcsfs",
    ]
)

pex_binary(
    name="ingest_sciscore_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
        "//3rdparty/python#pandas",
        "//3rdparty/python#google-apitools",
        "//3rdparty/python#openpyxl",
        "//3rdparty/python#fsspec",
        "//3rdparty/python#gcsfs",
    ]
)

python_distribution(
    name="ingest_sciscore_dist",
    dependencies=[
        ":ingest_sciscore",
    ],
    provides=python_artifact(
        name="ingest_sciscore_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="ingest_sciscore_runner",
    dependencies=[
        ":ingest_sciscore",
        ":ingest_sciscore_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
