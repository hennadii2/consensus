python_sources(
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
        "//3rdparty/python#pandas",
        "//3rdparty/python#google-apitools",
        "//3rdparty/python#openpyxl",
        "//3rdparty/python#fsspec",
        "//3rdparty/python#gcsfs",
        "//3rdparty/python#pip",
    ]
)

pex_binary(
    name="autocomplete_index_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
        "//3rdparty/python#pandas",
        "//3rdparty/python#google-apitools",
        "//3rdparty/python#openpyxl",
        "//3rdparty/python#fsspec",
        "//3rdparty/python#gcsfs",
        "//3rdparty/python#pip",
    ]
)

python_distribution(
    name="autocomplete_index_dist",
    dependencies=[
        ":autocomplete_index",
    ],
    provides=python_artifact(
        name="autocomplete_index_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="autocomplete_index_runner",
    dependencies=[
        ":autocomplete_index",
        ":autocomplete_index_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
