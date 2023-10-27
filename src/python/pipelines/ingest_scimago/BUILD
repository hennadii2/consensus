python_sources(
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
        "//3rdparty/python#pandas",
        "//3rdparty/python#fsspec",
        "//3rdparty/python#gcsfs",
        "//3rdparty/python#pip",
    ]
)

pex_binary(
    name="ingest_scimago_main",
    entry_point="main.py",
    # Enable this to run locally on M1/M2 Macs
    # environment="py39_local_arm64",
)

python_distribution(
    name="ingest_scimago_dist",
    dependencies=[
        ":ingest_scimago",
    ],
    provides=python_artifact(
        name="ingest_scimago_dist",
        version="1.0",
    ),
)

docker_image(
    name="ingest_scimago_runner",
    dependencies=[
        ":ingest_scimago",
        ":ingest_scimago_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
