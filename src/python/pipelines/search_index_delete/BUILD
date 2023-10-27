python_sources(
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ]
)

pex_binary(
    name="search_index_delete_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ]
)

python_distribution(
    name="search_index_delete_dist",
    dependencies=[
        ":search_index_delete",
    ],
    provides=python_artifact(
        name="search_index_delete_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="search_index_delete_runner",
    dependencies=[
        ":search_index_delete",
        ":search_index_delete_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
