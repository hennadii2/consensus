python_sources(
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ]
)

pex_binary(
    name="search_index_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ]
)

python_distribution(
    name="search_index_dist",
    dependencies=[
        ":search_index",
    ],
    provides=python_artifact(
        name="search_index_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="search_index_runner",
    dependencies=[
        ":search_index",
        ":search_index_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
