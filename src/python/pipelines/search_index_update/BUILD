python_sources(
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
        "//3rdparty/python#pip",
    ]
)

pex_binary(
    name="search_index_update_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ],
    # Enable this to run locally on M1/M2 Macs
    # environment="py39_local_arm64",
)

python_distribution(
    name="search_index_update_dist",
    dependencies=[
        ":search_index_update",
    ],
    provides=python_artifact(
        name="search_index_update_dist",
        version="1.0",
    ),
)

docker_image(
    name="search_index_update_runner",
    dependencies=[
        ":search_index_update",
        ":search_index_update_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
