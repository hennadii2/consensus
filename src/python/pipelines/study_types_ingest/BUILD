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
    name="study_types_ingest_main",
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
    name="study_types_ingest_dist",
    dependencies=[
        ":study_types_ingest",
    ],
    provides=python_artifact(
        name="study_types_ingest_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="study_types_ingest_runner",
    dependencies=[
        ":study_types_ingest",
        ":study_types_ingest_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
